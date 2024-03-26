#include <Python.h>
#include <time.h>

int c_nanosleep(int sec, long long nano) {
  int status = nanosleep((const struct timespec[]){{sec, nano}}, NULL);
  if (status == -1) {
    printf("nanosleep error: %s\n", strerror(errno));
  }
  return status;
}

static PyObject *py_nanosleep(PyObject *self, PyObject *args) {
  int sec;
  int status;
  long long nano;
  if (!PyArg_ParseTuple(args, "iL", &sec, &nano))
    return NULL;
  status = c_nanosleep(sec, nano);
  return PyLong_FromLong(status);
}

static PyObject *version(PyObject *self) {
  return Py_BuildValue("s", "Version 0.01");
}

static PyMethodDef Nanosleep[] = {
    {"py_nanosleep", py_nanosleep, METH_VARARGS,
     "Sleeps for amount in nanoseconds"},
    {"version", (PyCFunction)version, METH_NOARGS, "Returns version of module"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef Nsleep = {PyModuleDef_HEAD_INIT, "Nsleep",
                                    "py_nanosleep module", -1, Nanosleep};

PyMODINIT_FUNC PyInit_Nsleep(void) { return PyModule_Create(&Nsleep); }
