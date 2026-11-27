"""Bound subprocess trees on Windows, macOS and Linux using only the stdlib."""
from __future__ import annotations
import os
import signal
import subprocess
import tempfile
import threading
import time


class WindowsJob:
    """Assign a suspended process to a kill-on-close Job before it can spawn."""
    def __init__(self):
        import ctypes as c
        from ctypes import wintypes as w

        class Basic(c.Structure):
            _fields_ = [('process_time', c.c_int64), ('job_time', c.c_int64),
                        ('flags', w.DWORD), ('min_ws', c.c_size_t), ('max_ws', c.c_size_t),
                        ('active', w.DWORD), ('affinity', c.c_size_t),
                        ('priority', w.DWORD), ('scheduling', w.DWORD)]

        class IO(c.Structure):
            _fields_ = [(name, c.c_uint64) for name in ('read_ops', 'write_ops', 'other_ops',
                                                      'read_bytes', 'write_bytes', 'other_bytes')]

        class Limits(c.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_mem', c.c_size_t),
                        ('job_mem', c.c_size_t), ('peak_process', c.c_size_t), ('peak_job', c.c_size_t)]

        self.c = c
        self.api = c.WinDLL('kernel32', use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [c.c_void_p, w.LPCWSTR]
        self.api.CreateJobObjectW.restype = w.HANDLE
        self.api.SetInformationJobObject.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD]
        self.api.SetInformationJobObject.restype = w.BOOL
        self.api.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.api.AssignProcessToJobObject.restype = w.BOOL
        self.api.CloseHandle.argtypes = [w.HANDLE]
        self.api.CloseHandle.restype = w.BOOL
        self.api.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        self.api.TerminateJobObject.restype = w.BOOL
        self.api.QueryInformationJobObject.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p]
        self.api.QueryInformationJobObject.restype = w.BOOL
        class Accounting(c.Structure):
            _fields_ = [('user', c.c_int64), ('kernel', c.c_int64), ('period_user', c.c_int64),
                        ('period_kernel', c.c_int64), ('faults', w.DWORD), ('total', w.DWORD),
                        ('active', w.DWORD), ('terminated', w.DWORD)]
        self.accounting = Accounting
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise c.WinError(c.get_last_error())
        limits = Limits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle, 9, c.byref(limits), c.sizeof(limits)):
            error = c.WinError(c.get_last_error())
            self.close()
            raise error

    def attach_and_resume(self, proc):
        if not self.api.AssignProcessToJobObject(self.handle, int(proc._handle)):
            raise self.c.WinError(self.c.get_last_error())
        resume = self.c.WinDLL('ntdll').NtResumeProcess
        resume.argtypes = [self.c.c_void_p]
        resume.restype = self.c.c_long
        status = resume(int(proc._handle))
        if status:
            raise OSError(f'NtResumeProcess failed: {status}')

    def close(self):
        if self.handle:
            # Job termination is asynchronous. Wait for the accounting count
            # to drain before closing, so descendants release their cwd/files.
            self.api.TerminateJobObject(self.handle, 1)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                info = self.accounting()
                if not self.api.QueryInformationJobObject(self.handle, 1, self.c.byref(info), self.c.sizeof(info), None):
                    break
                if info.active == 0:
                    break
                time.sleep(.005)
            self.api.CloseHandle(self.handle)
            self.handle = None


def run_process(cmd, payload, cwd, stdout, stderr, timeout, stop, deadline=None):
    proc = job = input_file = None
    started = time.monotonic()
    try:
        if stop.is_set():
            return -1, 'cancelled'
        if deadline is not None and time.monotonic() >= deadline:
            return -1, 'timeout'
        # Windows communicate(input=...) writes stdin synchronously and can
        # block beyond its timeout if the child never reads. A regular input
        # file also avoids pipe backpressure on macOS/Linux.
        input_file = tempfile.TemporaryFile()
        input_file.write(payload)
        input_file.seek(0)
        if os.name == 'nt':
            job = WindowsJob()
            options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | 4}
        else:
            options = {'start_new_session': True}
        proc = subprocess.Popen(cmd, stdin=input_file, stdout=stdout, stderr=stderr,
                                cwd=str(cwd), **options)
        if job:
            job.attach_and_resume(proc)
        while True:
            remaining = timeout - (time.monotonic() - started)
            if deadline is not None:
                remaining = min(remaining, deadline - time.monotonic())
            if stop.is_set() or remaining <= 0:
                return -1, 'cancelled' if stop.is_set() else 'timeout'
            try:
                proc.wait(timeout=min(remaining, .2))
                return proc.returncode, None
            except subprocess.TimeoutExpired:
                pass
    except OSError as exc:
        return -2, f'process error: {exc}'
    finally:
        if job:
            job.close()
        elif proc is not None and os.name != 'nt':
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if proc is not None:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
        if input_file is not None:
            input_file.close()
