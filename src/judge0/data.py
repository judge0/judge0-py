from .base_types import LanguageAlias

LANGUAGE_TO_LANGUAGE_ID = {
    "1.13.1": {
        LanguageAlias.PYTHON: 71,
        LanguageAlias.CPP: 54,
        LanguageAlias.JAVA: 62,
        LanguageAlias.CPP_GCC: 54,
        LanguageAlias.CPP_CLANG: 76,
    },
    "1.13.1-extra": {
        LanguageAlias.PYTHON: 10,
        LanguageAlias.CPP: 2,
        LanguageAlias.JAVA: 4,
        LanguageAlias.CPP_CLANG: 2,
        LanguageAlias.PYTHON_FOR_ML: 10,
    },
    "1.14.0": {
        LanguageAlias.PYTHON: 100,
        LanguageAlias.CPP: 105,
        LanguageAlias.JAVA: 91,
        LanguageAlias.CPP_GCC: 105,
        LanguageAlias.CPP_CLANG: 76,
    },
    "1.14.0-extra": {
        LanguageAlias.PYTHON: 25,
        LanguageAlias.CPP: 2,
        LanguageAlias.JAVA: 4,
        LanguageAlias.CPP_CLANG: 2,
        LanguageAlias.PYTHON_FOR_ML: 25,
    },
}
