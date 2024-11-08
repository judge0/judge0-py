from .common import Language

LANGUAGE_TO_LANGUAGE_ID = {
    "1.13.1": {
        Language.PYTHON: 71,
        Language.CPP: 54,
        Language.JAVA: 62,
        Language.CPP_GCC: 54,
        Language.CPP_CLANG: 76,
    },
    "1.13.1-extra": {
        Language.PYTHON: 10,
        Language.CPP: 2,
        Language.JAVA: 4,
        Language.CPP_CLANG: 2,
        Language.PYTHON_FOR_ML: 10,
    },
    "1.14.0": {
        Language.PYTHON: 100,
        Language.CPP: 105,
        Language.JAVA: 91,
        Language.CPP_GCC: 105,
        Language.CPP_CLANG: 76,
    },
    "1.14.0-extra": {
        Language.PYTHON: 25,
        Language.CPP: 2,
        Language.JAVA: 4,
        Language.CPP_CLANG: 2,
        Language.PYTHON_FOR_ML: 25,
    },
}
