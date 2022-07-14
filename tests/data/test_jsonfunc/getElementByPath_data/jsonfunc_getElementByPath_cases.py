testcases = []

# ============================================================
# Dict is source
# One element
# Check for value and reference
jsonInput = \
[
    {
        "some_path": {"key": 1, "value": "ABC"}
    }
]

expected = \
[
    {"key": 1, "value": "ABC"}
]

testcases.append({'name': 'srcdict_one', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# Dict is source
# More than one element
# Check for value and reference
jsonInput = \
[
    {
        "some_path": {"key": 1, "value": "ABC"}
    },
    {
        "some_path": {"key": 2, "value": "ABC"}
    }
]

expected = \
[
    {"key": 1, "value": "ABC"},
    {"key": 2, "value": "ABC"}
]

testcases.append({'name': 'srcdict_many', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# List is source
# one element
# Check for value and reference
jsonInput = \
[
    [
        {
            "some_path": {"key": 1, "value": "ABC"}
        }
    ]
]

expected = \
[
    {"key": 1, "value": "ABC"}
]

testcases.append({'name': 'srclist_one', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# List is source
# More than one element
# Check for value and reference
jsonInput = \
[
    [
        {
            "some_path": {"key": 1, "value": "ABC"}
        }
    ],
    [
        {
            "some_path": {"key": 2, "value": "DEF"}
        }
    ]
]

expected = \
[
    {"key": 1, "value": "ABC"},
    {"key": 2, "value": "DEF"}
]

testcases.append({'name': 'srclist_many', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# List is source
# More than one elements
# Lists contain more than one dict
# Check for value and reference
jsonInput = \
[
    [
        {
            "some_path": {"key": 1, "value": "ABC"}
        },
        {
            "some_path": {"key": 2, "value": "DEF"}
        }
    ],
    [
        {
            "some_path": {"key": 3, "value": "GHI"}
        },
        {
            "some_path": {"key": 4, "value": "JKL"}
        }
    ]
]

expected = \
[
    {"key": 1, "value": "ABC"},
    {"key": 2, "value": "DEF"},
    {"key": 3, "value": "GHI"},
    {"key": 4, "value": "JKL"}
]

testcases.append({'name': 'srclist_many_many', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# Dict is source
# More than one elements
# Lists are found by path, they contain more than one dict
# Check for value and reference
jsonInput = \
[
    {
        "some_path": [
            {"some_path2": {"key": 1, "value": "ABC"}},
            {"some_path2": {"key": 2, "value": "DEF"}}
        ]
    },
    {
        "some_path": [
            {"some_path2": {"key": 3, "value": "GHI"}},
            {"some_path2": {"key": 4, "value": "JKL"}}
        ]
    }
]

expected = \
[
    [
        {"some_path2": {"key": 1, "value": "ABC"}},
        {"some_path2": {"key": 2, "value": "DEF"}}
    ],
    [
        {"some_path2": {"key": 3, "value": "GHI"}},
        {"some_path2": {"key": 4, "value": "JKL"}}
    ]
]

testcases.append({'name': 'srcdict_many_foundlist', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# Scalar (not dict or list) as source must be ignored
jsonInput = \
[
    {
        "some_path": {"key": 1, "value": "ABC"}
    },
    "not_dict_or_list"
]

expected = \
[
    {"key": 1, "value": "ABC"}
]

testcases.append({'name': 'ignore_srcscalar', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# Scalar (not dict or list) as found must be ignored
jsonInput = \
[
    {
        "some_path": {"key": 1, "value": "ABC"}
    },
    {
        "some_path": "not_dict_or_list"
    }
]

expected = \
[
    {"key": 1, "value": "ABC"}
]

testcases.append({'name': 'ignore_foundscalar', 'jsonInput': jsonInput, 'expected': expected})

# ============================================================
# Ignore found elements if they are not of the same type as the first found
jsonInput = \
[
    {
        "some_path": {"key": 1, "value": "ABC"}
    },
    {
        "some_path": [
            {"key": 2, "value": "DEF"},
            {"key": 3, "value": "GHI"}
        ]
    },
    {
        "some_path": {"key": 4, "value": "JKL"}
    }
]

expected = \
[
    {"key": 1, "value": "ABC"},
    {"key": 4, "value": "JKL"}
]

testcases.append({'name': 'found_diff_types', 'jsonInput': jsonInput, 'expected': expected})
