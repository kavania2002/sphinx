"""Tests util.typing functions."""

import dataclasses
import sys
import typing as t
from collections import abc
from contextvars import Context, ContextVar, Token
from enum import Enum
from numbers import Integral
from struct import Struct
from types import (
    AsyncGeneratorType,
    BuiltinFunctionType,
    BuiltinMethodType,
    CellType,
    ClassMethodDescriptorType,
    CodeType,
    CoroutineType,
    FrameType,
    FunctionType,
    GeneratorType,
    GetSetDescriptorType,
    LambdaType,
    MappingProxyType,
    MemberDescriptorType,
    MethodDescriptorType,
    MethodType,
    MethodWrapperType,
    ModuleType,
    TracebackType,
    WrapperDescriptorType,
)
from typing import (
    Annotated,
    Any,
    Dict,
    ForwardRef,
    List,
    Literal,
    NewType,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import pytest

from sphinx.ext.autodoc import mock
from sphinx.util.typing import _INVALID_BUILTIN_CLASSES, restify, stringify_annotation


class MyClass1:
    pass


class MyClass2(MyClass1):
    __qualname__ = '<MyClass2>'


class MyEnum(Enum):
    a = 1


T = TypeVar('T')
MyInt = NewType('MyInt', int)


class MyList(List[T]):
    pass


class BrokenType:
    __args__ = int


@dataclasses.dataclass(frozen=True)
class Gt:
    gt: float


def test_restify():
    assert restify(int) == ":py:class:`int`"
    assert restify(int, "smart") == ":py:class:`int`"

    assert restify(str) == ":py:class:`str`"
    assert restify(str, "smart") == ":py:class:`str`"

    assert restify(None) == ":py:obj:`None`"
    assert restify(None, "smart") == ":py:obj:`None`"

    assert restify(Integral) == ":py:class:`numbers.Integral`"
    assert restify(Integral, "smart") == ":py:class:`~numbers.Integral`"

    assert restify(Struct) == ":py:class:`struct.Struct`"
    assert restify(Struct, "smart") == ":py:class:`~struct.Struct`"

    assert restify(TracebackType) == ":py:class:`types.TracebackType`"
    assert restify(TracebackType, "smart") == ":py:class:`~types.TracebackType`"

    assert restify(Any) == ":py:obj:`~typing.Any`"
    assert restify(Any, "smart") == ":py:obj:`~typing.Any`"

    assert restify('str') == "str"
    assert restify('str', "smart") == "str"


def test_is_invalid_builtin_class():
    # if these tests start failing, it means that the __module__
    # of one of these classes has changed, and _INVALID_BUILTIN_CLASSES
    # in sphinx.util.typing needs to be updated.
    assert _INVALID_BUILTIN_CLASSES.keys() == {
        Context,
        ContextVar,
        Token,
        Struct,
        AsyncGeneratorType,
        BuiltinFunctionType,
        BuiltinMethodType,
        CellType,
        ClassMethodDescriptorType,
        CodeType,
        CoroutineType,
        FrameType,
        FunctionType,
        GeneratorType,
        GetSetDescriptorType,
        LambdaType,
        MappingProxyType,
        MemberDescriptorType,
        MethodDescriptorType,
        MethodType,
        MethodWrapperType,
        ModuleType,
        TracebackType,
        WrapperDescriptorType,
    }
    assert Struct.__module__ == '_struct'
    assert AsyncGeneratorType.__module__ == 'builtins'
    assert BuiltinFunctionType.__module__ == 'builtins'
    assert BuiltinMethodType.__module__ == 'builtins'
    assert CellType.__module__ == 'builtins'
    assert ClassMethodDescriptorType.__module__ == 'builtins'
    assert CodeType.__module__ == 'builtins'
    assert CoroutineType.__module__ == 'builtins'
    assert FrameType.__module__ == 'builtins'
    assert FunctionType.__module__ == 'builtins'
    assert GeneratorType.__module__ == 'builtins'
    assert GetSetDescriptorType.__module__ == 'builtins'
    assert LambdaType.__module__ == 'builtins'
    assert MappingProxyType.__module__ == 'builtins'
    assert MemberDescriptorType.__module__ == 'builtins'
    assert MethodDescriptorType.__module__ == 'builtins'
    assert MethodType.__module__ == 'builtins'
    assert MethodWrapperType.__module__ == 'builtins'
    assert ModuleType.__module__ == 'builtins'
    assert TracebackType.__module__ == 'builtins'
    assert WrapperDescriptorType.__module__ == 'builtins'


def test_restify_type_hints_containers():
    assert restify(List) == ":py:class:`~typing.List`"
    assert restify(Dict) == ":py:class:`~typing.Dict`"
    assert restify(List[int]) == ":py:class:`~typing.List`\\ [:py:class:`int`]"
    assert restify(List[str]) == ":py:class:`~typing.List`\\ [:py:class:`str`]"
    assert restify(Dict[str, float]) == (":py:class:`~typing.Dict`\\ "
                                         "[:py:class:`str`, :py:class:`float`]")
    assert restify(Tuple[str, str, str]) == (":py:class:`~typing.Tuple`\\ "
                                             "[:py:class:`str`, :py:class:`str`, "
                                             ":py:class:`str`]")
    assert restify(Tuple[str, ...]) == ":py:class:`~typing.Tuple`\\ [:py:class:`str`, ...]"

    if sys.version_info[:2] <= (3, 10):
        assert restify(Tuple[()]) == ":py:class:`~typing.Tuple`\\ [()]"
    else:
        assert restify(Tuple[()]) == ":py:class:`~typing.Tuple`"

    assert restify(List[Dict[str, Tuple]]) == (":py:class:`~typing.List`\\ "
                                               "[:py:class:`~typing.Dict`\\ "
                                               "[:py:class:`str`, :py:class:`~typing.Tuple`]]")
    assert restify(MyList[Tuple[int, int]]) == (":py:class:`tests.test_util.test_util_typing.MyList`\\ "
                                                "[:py:class:`~typing.Tuple`\\ "
                                                "[:py:class:`int`, :py:class:`int`]]")
    assert restify(t.Generator[None, None, None]) == (":py:class:`~typing.Generator`\\ "
                                                      "[:py:obj:`None`, :py:obj:`None`, "
                                                      ":py:obj:`None`]")
    assert restify(abc.Generator[None, None, None]) == (":py:class:`collections.abc.Generator`\\ "
                                                        "[:py:obj:`None`, :py:obj:`None`, "
                                                        ":py:obj:`None`]")
    assert restify(t.Iterator[None]) == (":py:class:`~typing.Iterator`\\ "
                                         "[:py:obj:`None`]")
    assert restify(abc.Iterator[None]) == (":py:class:`collections.abc.Iterator`\\ "
                                           "[:py:obj:`None`]")


def test_restify_Annotated():
    assert restify(Annotated[str, "foo", "bar"]) == ":py:class:`~typing.Annotated`\\ [:py:class:`str`, 'foo', 'bar']"
    assert restify(Annotated[str, "foo", "bar"], 'smart') == ":py:class:`~typing.Annotated`\\ [:py:class:`str`, 'foo', 'bar']"
    assert restify(Annotated[float, Gt(-10.0)]) == ':py:class:`~typing.Annotated`\\ [:py:class:`float`, Gt(gt=-10.0)]'
    assert restify(Annotated[float, Gt(-10.0)], 'smart') == ':py:class:`~typing.Annotated`\\ [:py:class:`float`, Gt(gt=-10.0)]'


def test_restify_type_hints_Callable():
    assert restify(t.Callable) == ":py:class:`~typing.Callable`"
    assert restify(t.Callable[[str], int]) == (":py:class:`~typing.Callable`\\ "
                                               "[[:py:class:`str`], :py:class:`int`]")
    assert restify(t.Callable[..., int]) == (":py:class:`~typing.Callable`\\ "
                                             "[[...], :py:class:`int`]")
    assert restify(abc.Callable) == ":py:class:`collections.abc.Callable`"
    assert restify(abc.Callable[[str], int]) == (":py:class:`collections.abc.Callable`\\ "
                                                 "[[:py:class:`str`], :py:class:`int`]")
    assert restify(abc.Callable[..., int]) == (":py:class:`collections.abc.Callable`\\ "
                                               "[[...], :py:class:`int`]")


def test_restify_type_hints_Union():
    assert restify(Union[int]) == ":py:class:`int`"
    assert restify(Union[int, str]) == ":py:class:`int` | :py:class:`str`"
    assert restify(Optional[int]) == ":py:class:`int` | :py:obj:`None`"

    assert restify(Union[str, None]) == ":py:class:`str` | :py:obj:`None`"
    assert restify(Union[None, str]) == ":py:obj:`None` | :py:class:`str`"
    assert restify(Optional[str]) == ":py:class:`str` | :py:obj:`None`"

    assert restify(Union[int, str, None]) == (
        ":py:class:`int` | :py:class:`str` | :py:obj:`None`"
    )
    assert restify(Optional[Union[int, str]]) in {
        ":py:class:`str` | :py:class:`int` | :py:obj:`None`",
        ":py:class:`int` | :py:class:`str` | :py:obj:`None`",
    }

    assert restify(Union[int, Integral]) == (
        ":py:class:`int` | :py:class:`numbers.Integral`"
    )
    assert restify(Union[int, Integral], "smart") == (
        ":py:class:`int` | :py:class:`~numbers.Integral`"
    )

    assert (restify(Union[MyClass1, MyClass2]) ==
            (":py:class:`tests.test_util.test_util_typing.MyClass1`"
             " | :py:class:`tests.test_util.test_util_typing.<MyClass2>`"))
    assert (restify(Union[MyClass1, MyClass2], "smart") ==
            (":py:class:`~tests.test_util.test_util_typing.MyClass1`"
             " | :py:class:`~tests.test_util.test_util_typing.<MyClass2>`"))

    assert (restify(Optional[Union[MyClass1, MyClass2]]) ==
            (":py:class:`tests.test_util.test_util_typing.MyClass1`"
             " | :py:class:`tests.test_util.test_util_typing.<MyClass2>`"
             " | :py:obj:`None`"))
    assert (restify(Optional[Union[MyClass1, MyClass2]], "smart") ==
            (":py:class:`~tests.test_util.test_util_typing.MyClass1`"
             " | :py:class:`~tests.test_util.test_util_typing.<MyClass2>`"
             " | :py:obj:`None`"))


def test_restify_type_hints_typevars():
    T = TypeVar('T')
    T_co = TypeVar('T_co', covariant=True)
    T_contra = TypeVar('T_contra', contravariant=True)

    assert restify(T) == ":py:obj:`tests.test_util.test_util_typing.T`"
    assert restify(T, "smart") == ":py:obj:`~tests.test_util.test_util_typing.T`"

    assert restify(T_co) == ":py:obj:`tests.test_util.test_util_typing.T_co`"
    assert restify(T_co, "smart") == ":py:obj:`~tests.test_util.test_util_typing.T_co`"

    assert restify(T_contra) == ":py:obj:`tests.test_util.test_util_typing.T_contra`"
    assert restify(T_contra, "smart") == ":py:obj:`~tests.test_util.test_util_typing.T_contra`"

    assert restify(List[T]) == ":py:class:`~typing.List`\\ [:py:obj:`tests.test_util.test_util_typing.T`]"
    assert restify(List[T], "smart") == ":py:class:`~typing.List`\\ [:py:obj:`~tests.test_util.test_util_typing.T`]"

    assert restify(list[T]) == ":py:class:`list`\\ [:py:obj:`tests.test_util.test_util_typing.T`]"
    assert restify(list[T], "smart") == ":py:class:`list`\\ [:py:obj:`~tests.test_util.test_util_typing.T`]"

    if sys.version_info[:2] >= (3, 10):
        assert restify(MyInt) == ":py:class:`tests.test_util.test_util_typing.MyInt`"
        assert restify(MyInt, "smart") == ":py:class:`~tests.test_util.test_util_typing.MyInt`"
    else:
        assert restify(MyInt) == ":py:class:`MyInt`"
        assert restify(MyInt, "smart") == ":py:class:`MyInt`"


def test_restify_type_hints_custom_class():
    assert restify(MyClass1) == ":py:class:`tests.test_util.test_util_typing.MyClass1`"
    assert restify(MyClass1, "smart") == ":py:class:`~tests.test_util.test_util_typing.MyClass1`"

    assert restify(MyClass2) == ":py:class:`tests.test_util.test_util_typing.<MyClass2>`"
    assert restify(MyClass2, "smart") == ":py:class:`~tests.test_util.test_util_typing.<MyClass2>`"


def test_restify_type_hints_alias():
    MyStr = str
    MyTypingTuple = Tuple[str, str]
    MyTuple = tuple[str, str]
    assert restify(MyStr) == ":py:class:`str`"
    assert restify(MyTypingTuple) == ":py:class:`~typing.Tuple`\\ [:py:class:`str`, :py:class:`str`]"
    assert restify(MyTuple) == ":py:class:`tuple`\\ [:py:class:`str`, :py:class:`str`]"


def test_restify_type_ForwardRef():
    assert restify(ForwardRef("MyInt")) == ":py:class:`MyInt`"

    assert restify(list[ForwardRef("MyInt")]) == ":py:class:`list`\\ [:py:class:`MyInt`]"

    assert restify(Tuple[dict[ForwardRef("MyInt"), str], list[List[int]]]) == ":py:class:`~typing.Tuple`\\ [:py:class:`dict`\\ [:py:class:`MyInt`, :py:class:`str`], :py:class:`list`\\ [:py:class:`~typing.List`\\ [:py:class:`int`]]]"  # type: ignore[attr-defined]


def test_restify_type_Literal():
    assert restify(Literal[1, "2", "\r"]) == ":py:obj:`~typing.Literal`\\ [1, '2', '\\r']"

    assert restify(Literal[MyEnum.a], 'fully-qualified-except-typing') == ':py:obj:`~typing.Literal`\\ [:py:attr:`tests.test_util.test_util_typing.MyEnum.a`]'
    assert restify(Literal[MyEnum.a], 'smart') == ':py:obj:`~typing.Literal`\\ [:py:attr:`~tests.test_util.test_util_typing.MyEnum.a`]'


def test_restify_pep_585():
    assert restify(list[str]) == ":py:class:`list`\\ [:py:class:`str`]"  # type: ignore[attr-defined]
    assert restify(dict[str, str]) == (":py:class:`dict`\\ "  # type: ignore[attr-defined]
                                       "[:py:class:`str`, :py:class:`str`]")
    assert restify(tuple[str, ...]) == ":py:class:`tuple`\\ [:py:class:`str`, ...]"
    assert restify(tuple[str, str, str]) == (":py:class:`tuple`\\ "
                                             "[:py:class:`str`, :py:class:`str`, "
                                             ":py:class:`str`]")
    assert restify(dict[str, tuple[int, ...]]) == (":py:class:`dict`\\ "  # type: ignore[attr-defined]
                                                   "[:py:class:`str`, :py:class:`tuple`\\ "
                                                   "[:py:class:`int`, ...]]")

    assert restify(tuple[()]) == ":py:class:`tuple`\\ [()]"

    # Mix old typing with PEP 585
    assert restify(List[dict[str, Tuple[str, ...]]]) == (":py:class:`~typing.List`\\ "
                                                         "[:py:class:`dict`\\ "
                                                         "[:py:class:`str`, :py:class:`~typing.Tuple`\\ "
                                                         "[:py:class:`str`, ...]]]")
    assert restify(tuple[MyList[list[int]], int]) == (":py:class:`tuple`\\ ["
                                                      ":py:class:`tests.test_util.test_util_typing.MyList`\\ "
                                                      "[:py:class:`list`\\ [:py:class:`int`]], "
                                                      ":py:class:`int`]")


def test_restify_Unpack():
    from typing_extensions import Unpack as UnpackCompat

    class X(t.TypedDict):
        x: int
        y: int
        label: str

    # Unpack is considered as typing special form so we always have '~'
    if sys.version_info[:2] >= (3, 12):
        expect = r':py:obj:`~typing.Unpack`\ [:py:class:`X`]'
        assert restify(UnpackCompat['X'], 'fully-qualified-except-typing') == expect
        assert restify(UnpackCompat['X'], 'smart') == expect
    else:
        expect = r':py:obj:`~typing_extensions.Unpack`\ [:py:class:`X`]'
        assert restify(UnpackCompat['X'], 'fully-qualified-except-typing') == expect
        assert restify(UnpackCompat['X'], 'smart') == expect

    if sys.version_info[:2] >= (3, 11):
        expect = r':py:obj:`~typing.Unpack`\ [:py:class:`X`]'
        assert restify(t.Unpack['X'], 'fully-qualified-except-typing') == expect
        assert restify(t.Unpack['X'], 'smart') == expect


@pytest.mark.skipif(sys.version_info[:2] <= (3, 9), reason='python 3.10+ is required.')
def test_restify_type_union_operator():
    assert restify(int | None) == ":py:class:`int` | :py:obj:`None`"  # type: ignore[attr-defined]
    assert restify(None | int) == ":py:obj:`None` | :py:class:`int`"  # type: ignore[attr-defined]
    assert restify(int | str) == ":py:class:`int` | :py:class:`str`"  # type: ignore[attr-defined]
    assert restify(int | str | None) == (":py:class:`int` | :py:class:`str` | "  # type: ignore[attr-defined]
                                         ":py:obj:`None`")


def test_restify_broken_type_hints():
    assert restify(BrokenType) == ':py:class:`tests.test_util.test_util_typing.BrokenType`'
    assert restify(BrokenType, "smart") == ':py:class:`~tests.test_util.test_util_typing.BrokenType`'


def test_restify_mock():
    with mock(['unknown']):
        import unknown
        assert restify(unknown) == ':py:class:`unknown`'
        assert restify(unknown.secret.Class) == ':py:class:`unknown.secret.Class`'
        assert restify(unknown.secret.Class, "smart") == ':py:class:`~unknown.secret.Class`'


def test_stringify_annotation():
    assert stringify_annotation(int, 'fully-qualified-except-typing') == "int"
    assert stringify_annotation(int, "smart") == "int"

    assert stringify_annotation(str, 'fully-qualified-except-typing') == "str"
    assert stringify_annotation(str, "smart") == "str"

    assert stringify_annotation(None, 'fully-qualified-except-typing') == "None"
    assert stringify_annotation(None, "smart") == "None"

    assert stringify_annotation(Integral, 'fully-qualified-except-typing') == "numbers.Integral"
    assert stringify_annotation(Integral, "smart") == "~numbers.Integral"

    assert stringify_annotation(Struct, 'fully-qualified-except-typing') == "struct.Struct"
    assert stringify_annotation(Struct, "smart") == "~struct.Struct"

    assert stringify_annotation(TracebackType, 'fully-qualified-except-typing') == "types.TracebackType"
    assert stringify_annotation(TracebackType, "smart") == "~types.TracebackType"

    assert stringify_annotation(Any, 'fully-qualified-except-typing') == "Any"
    assert stringify_annotation(Any, "fully-qualified") == "typing.Any"
    assert stringify_annotation(Any, "smart") == "~typing.Any"


def test_stringify_type_hints_containers():
    assert stringify_annotation(List, 'fully-qualified-except-typing') == "List"
    assert stringify_annotation(List, "fully-qualified") == "typing.List"
    assert stringify_annotation(List, "smart") == "~typing.List"

    assert stringify_annotation(Dict, 'fully-qualified-except-typing') == "Dict"
    assert stringify_annotation(Dict, "fully-qualified") == "typing.Dict"
    assert stringify_annotation(Dict, "smart") == "~typing.Dict"

    assert stringify_annotation(List[int], 'fully-qualified-except-typing') == "List[int]"
    assert stringify_annotation(List[int], "fully-qualified") == "typing.List[int]"
    assert stringify_annotation(List[int], "smart") == "~typing.List[int]"

    assert stringify_annotation(List[str], 'fully-qualified-except-typing') == "List[str]"
    assert stringify_annotation(List[str], "fully-qualified") == "typing.List[str]"
    assert stringify_annotation(List[str], "smart") == "~typing.List[str]"

    assert stringify_annotation(Dict[str, float], 'fully-qualified-except-typing') == "Dict[str, float]"
    assert stringify_annotation(Dict[str, float], "fully-qualified") == "typing.Dict[str, float]"
    assert stringify_annotation(Dict[str, float], "smart") == "~typing.Dict[str, float]"

    assert stringify_annotation(Tuple[str, str, str], 'fully-qualified-except-typing') == "Tuple[str, str, str]"
    assert stringify_annotation(Tuple[str, str, str], "fully-qualified") == "typing.Tuple[str, str, str]"
    assert stringify_annotation(Tuple[str, str, str], "smart") == "~typing.Tuple[str, str, str]"

    assert stringify_annotation(Tuple[str, ...], 'fully-qualified-except-typing') == "Tuple[str, ...]"
    assert stringify_annotation(Tuple[str, ...], "fully-qualified") == "typing.Tuple[str, ...]"
    assert stringify_annotation(Tuple[str, ...], "smart") == "~typing.Tuple[str, ...]"

    if sys.version_info[:2] <= (3, 10):
        assert stringify_annotation(Tuple[()], 'fully-qualified-except-typing') == "Tuple[()]"
        assert stringify_annotation(Tuple[()], "fully-qualified") == "typing.Tuple[()]"
        assert stringify_annotation(Tuple[()], "smart") == "~typing.Tuple[()]"
    else:
        assert stringify_annotation(Tuple[()], 'fully-qualified-except-typing') == "Tuple"
        assert stringify_annotation(Tuple[()], "fully-qualified") == "typing.Tuple"
        assert stringify_annotation(Tuple[()], "smart") == "~typing.Tuple"

    assert stringify_annotation(List[Dict[str, Tuple]], 'fully-qualified-except-typing') == "List[Dict[str, Tuple]]"
    assert stringify_annotation(List[Dict[str, Tuple]], "fully-qualified") == "typing.List[typing.Dict[str, typing.Tuple]]"
    assert stringify_annotation(List[Dict[str, Tuple]], "smart") == "~typing.List[~typing.Dict[str, ~typing.Tuple]]"

    assert stringify_annotation(MyList[Tuple[int, int]], 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.MyList[Tuple[int, int]]"
    assert stringify_annotation(MyList[Tuple[int, int]], "fully-qualified") == "tests.test_util.test_util_typing.MyList[typing.Tuple[int, int]]"
    assert stringify_annotation(MyList[Tuple[int, int]], "smart") == "~tests.test_util.test_util_typing.MyList[~typing.Tuple[int, int]]"

    assert stringify_annotation(t.Generator[None, None, None], 'fully-qualified-except-typing') == "Generator[None, None, None]"
    assert stringify_annotation(t.Generator[None, None, None], "fully-qualified") == "typing.Generator[None, None, None]"
    assert stringify_annotation(t.Generator[None, None, None], "smart") == "~typing.Generator[None, None, None]"

    assert stringify_annotation(abc.Generator[None, None, None], 'fully-qualified-except-typing') == "collections.abc.Generator[None, None, None]"
    assert stringify_annotation(abc.Generator[None, None, None], "fully-qualified") == "collections.abc.Generator[None, None, None]"
    assert stringify_annotation(abc.Generator[None, None, None], "smart") == "~collections.abc.Generator[None, None, None]"

    assert stringify_annotation(t.Iterator[None], 'fully-qualified-except-typing') == "Iterator[None]"
    assert stringify_annotation(t.Iterator[None], "fully-qualified") == "typing.Iterator[None]"
    assert stringify_annotation(t.Iterator[None], "smart") == "~typing.Iterator[None]"

    assert stringify_annotation(abc.Iterator[None], 'fully-qualified-except-typing') == "collections.abc.Iterator[None]"
    assert stringify_annotation(abc.Iterator[None], "fully-qualified") == "collections.abc.Iterator[None]"
    assert stringify_annotation(abc.Iterator[None], "smart") == "~collections.abc.Iterator[None]"


def test_stringify_type_hints_pep_585():
    assert stringify_annotation(list[int], 'fully-qualified-except-typing') == "list[int]"
    assert stringify_annotation(list[int], "smart") == "list[int]"

    assert stringify_annotation(list[str], 'fully-qualified-except-typing') == "list[str]"
    assert stringify_annotation(list[str], "smart") == "list[str]"

    assert stringify_annotation(dict[str, float], 'fully-qualified-except-typing') == "dict[str, float]"
    assert stringify_annotation(dict[str, float], "smart") == "dict[str, float]"

    assert stringify_annotation(tuple[str, str, str], 'fully-qualified-except-typing') == "tuple[str, str, str]"
    assert stringify_annotation(tuple[str, str, str], "smart") == "tuple[str, str, str]"

    assert stringify_annotation(tuple[str, ...], 'fully-qualified-except-typing') == "tuple[str, ...]"
    assert stringify_annotation(tuple[str, ...], "smart") == "tuple[str, ...]"

    assert stringify_annotation(tuple[()], 'fully-qualified-except-typing') == "tuple[()]"
    assert stringify_annotation(tuple[()], "smart") == "tuple[()]"

    assert stringify_annotation(list[dict[str, tuple]], 'fully-qualified-except-typing') == "list[dict[str, tuple]]"
    assert stringify_annotation(list[dict[str, tuple]], "smart") == "list[dict[str, tuple]]"

    assert stringify_annotation(MyList[tuple[int, int]], 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.MyList[tuple[int, int]]"
    assert stringify_annotation(MyList[tuple[int, int]], "fully-qualified") == "tests.test_util.test_util_typing.MyList[tuple[int, int]]"
    assert stringify_annotation(MyList[tuple[int, int]], "smart") == "~tests.test_util.test_util_typing.MyList[tuple[int, int]]"

    assert stringify_annotation(type[int], 'fully-qualified-except-typing') == "type[int]"
    assert stringify_annotation(type[int], "smart") == "type[int]"

    # Mix typing and pep 585
    assert stringify_annotation(tuple[List[dict[int, str]], str, ...], 'fully-qualified-except-typing') == "tuple[List[dict[int, str]], str, ...]"
    assert stringify_annotation(tuple[List[dict[int, str]], str, ...], "smart") == "tuple[~typing.List[dict[int, str]], str, ...]"


@pytest.mark.xfail(sys.version_info[:2] <= (3, 9), reason='Needs fixing.')
def test_stringify_Annotated():
    assert stringify_annotation(Annotated[str, "foo", "bar"], 'fully-qualified-except-typing') == "Annotated[str, 'foo', 'bar']"
    assert stringify_annotation(Annotated[str, "foo", "bar"], 'smart') == "~typing.Annotated[str, 'foo', 'bar']"
    assert stringify_annotation(Annotated[float, Gt(-10.0)], 'fully-qualified-except-typing') == "Annotated[float, Gt(gt=-10.0)]"
    assert stringify_annotation(Annotated[float, Gt(-10.0)], 'smart') == "~typing.Annotated[float, Gt(gt=-10.0)]"


def test_stringify_Unpack():
    from typing_extensions import Unpack as UnpackCompat

    class X(t.TypedDict):
        x: int
        y: int
        label: str

    if sys.version_info[:2] >= (3, 11):
        # typing.Unpack is introduced in 3.11 but typing_extensions.Unpack only
        # uses typing.Unpack in 3.12+, so the objects are not synchronised with
        # each other, but we will assume that users use typing.Unpack.
        import typing

        UnpackCompat = typing.Unpack  # NoQA: F811
        assert stringify_annotation(UnpackCompat['X']) == 'Unpack[X]'
        assert stringify_annotation(UnpackCompat['X'], 'smart') == '~typing.Unpack[X]'
    else:
        assert stringify_annotation(UnpackCompat['X']) == 'typing_extensions.Unpack[X]'
        assert stringify_annotation(UnpackCompat['X'], 'smart') == '~typing_extensions.Unpack[X]'

    if sys.version_info[:2] >= (3, 11):
        assert stringify_annotation(t.Unpack['X']) == 'Unpack[X]'
        assert stringify_annotation(t.Unpack['X'], 'smart') == '~typing.Unpack[X]'


def test_stringify_type_hints_string():
    assert stringify_annotation("int", 'fully-qualified-except-typing') == "int"
    assert stringify_annotation("int", 'fully-qualified') == "int"
    assert stringify_annotation("int", "smart") == "int"

    assert stringify_annotation("str", 'fully-qualified-except-typing') == "str"
    assert stringify_annotation("str", 'fully-qualified') == "str"
    assert stringify_annotation("str", "smart") == "str"

    assert stringify_annotation(List["int"], 'fully-qualified-except-typing') == "List[int]"
    assert stringify_annotation(List["int"], 'fully-qualified') == "typing.List[int]"
    assert stringify_annotation(List["int"], "smart") == "~typing.List[int]"

    assert stringify_annotation(list["int"], 'fully-qualified-except-typing') == "list[int]"
    assert stringify_annotation(list["int"], 'fully-qualified') == "list[int]"
    assert stringify_annotation(list["int"], "smart") == "list[int]"

    assert stringify_annotation("Tuple[str]", 'fully-qualified-except-typing') == "Tuple[str]"
    assert stringify_annotation("Tuple[str]", 'fully-qualified') == "Tuple[str]"
    assert stringify_annotation("Tuple[str]", "smart") == "Tuple[str]"

    assert stringify_annotation("tuple[str]", 'fully-qualified-except-typing') == "tuple[str]"
    assert stringify_annotation("tuple[str]", 'fully-qualified') == "tuple[str]"
    assert stringify_annotation("tuple[str]", "smart") == "tuple[str]"

    assert stringify_annotation("unknown", 'fully-qualified-except-typing') == "unknown"
    assert stringify_annotation("unknown", 'fully-qualified') == "unknown"
    assert stringify_annotation("unknown", "smart") == "unknown"


def test_stringify_type_hints_Callable():
    assert stringify_annotation(t.Callable, 'fully-qualified-except-typing') == "Callable"
    assert stringify_annotation(t.Callable, "fully-qualified") == "typing.Callable"
    assert stringify_annotation(t.Callable, "smart") == "~typing.Callable"

    assert stringify_annotation(t.Callable[[str], int], 'fully-qualified-except-typing') == "Callable[[str], int]"
    assert stringify_annotation(t.Callable[[str], int], "fully-qualified") == "typing.Callable[[str], int]"
    assert stringify_annotation(t.Callable[[str], int], "smart") == "~typing.Callable[[str], int]"

    assert stringify_annotation(t.Callable[..., int], 'fully-qualified-except-typing') == "Callable[[...], int]"
    assert stringify_annotation(t.Callable[..., int], "fully-qualified") == "typing.Callable[[...], int]"
    assert stringify_annotation(t.Callable[..., int], "smart") == "~typing.Callable[[...], int]"

    assert stringify_annotation(abc.Callable, 'fully-qualified-except-typing') == "collections.abc.Callable"
    assert stringify_annotation(abc.Callable, "fully-qualified") == "collections.abc.Callable"
    assert stringify_annotation(abc.Callable, "smart") == "~collections.abc.Callable"

    assert stringify_annotation(abc.Callable[[str], int], 'fully-qualified-except-typing') == "collections.abc.Callable[[str], int]"
    assert stringify_annotation(abc.Callable[[str], int], "fully-qualified") == "collections.abc.Callable[[str], int]"
    assert stringify_annotation(abc.Callable[[str], int], "smart") == "~collections.abc.Callable[[str], int]"

    assert stringify_annotation(abc.Callable[..., int], 'fully-qualified-except-typing') == "collections.abc.Callable[[...], int]"
    assert stringify_annotation(abc.Callable[..., int], "fully-qualified") == "collections.abc.Callable[[...], int]"
    assert stringify_annotation(abc.Callable[..., int], "smart") == "~collections.abc.Callable[[...], int]"


def test_stringify_type_hints_Union():
    assert stringify_annotation(Optional[int], 'fully-qualified-except-typing') == "int | None"
    assert stringify_annotation(Optional[int], "fully-qualified") == "int | None"
    assert stringify_annotation(Optional[int], "smart") == "int | None"

    assert stringify_annotation(Union[int, None], 'fully-qualified-except-typing') == "int | None"
    assert stringify_annotation(Union[None, int], 'fully-qualified-except-typing') == "None | int"
    assert stringify_annotation(Union[int, None], "fully-qualified") == "int | None"
    assert stringify_annotation(Union[None, int], "fully-qualified") == "None | int"
    assert stringify_annotation(Union[int, None], "smart") == "int | None"
    assert stringify_annotation(Union[None, int], "smart") == "None | int"

    assert stringify_annotation(Union[int, str], 'fully-qualified-except-typing') == "int | str"
    assert stringify_annotation(Union[int, str], "fully-qualified") == "int | str"
    assert stringify_annotation(Union[int, str], "smart") == "int | str"

    assert stringify_annotation(Union[int, Integral], 'fully-qualified-except-typing') == "int | numbers.Integral"
    assert stringify_annotation(Union[int, Integral], "fully-qualified") == "int | numbers.Integral"
    assert stringify_annotation(Union[int, Integral], "smart") == "int | ~numbers.Integral"

    assert (stringify_annotation(Union[MyClass1, MyClass2], 'fully-qualified-except-typing') ==
            "tests.test_util.test_util_typing.MyClass1 | tests.test_util.test_util_typing.<MyClass2>")
    assert (stringify_annotation(Union[MyClass1, MyClass2], "fully-qualified") ==
            "tests.test_util.test_util_typing.MyClass1 | tests.test_util.test_util_typing.<MyClass2>")
    assert (stringify_annotation(Union[MyClass1, MyClass2], "smart") ==
            "~tests.test_util.test_util_typing.MyClass1 | ~tests.test_util.test_util_typing.<MyClass2>")


def test_stringify_type_hints_typevars():
    T = TypeVar('T')
    T_co = TypeVar('T_co', covariant=True)
    T_contra = TypeVar('T_contra', contravariant=True)

    assert stringify_annotation(T, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.T"
    assert stringify_annotation(T, "smart") == "~tests.test_util.test_util_typing.T"

    assert stringify_annotation(T_co, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.T_co"
    assert stringify_annotation(T_co, "smart") == "~tests.test_util.test_util_typing.T_co"

    assert stringify_annotation(T_contra, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.T_contra"
    assert stringify_annotation(T_contra, "smart") == "~tests.test_util.test_util_typing.T_contra"

    assert stringify_annotation(List[T], 'fully-qualified-except-typing') == "List[tests.test_util.test_util_typing.T]"
    assert stringify_annotation(List[T], "smart") == "~typing.List[~tests.test_util.test_util_typing.T]"

    assert stringify_annotation(list[T], 'fully-qualified-except-typing') == "list[tests.test_util.test_util_typing.T]"
    assert stringify_annotation(list[T], "smart") == "list[~tests.test_util.test_util_typing.T]"

    if sys.version_info[:2] >= (3, 10):
        assert stringify_annotation(MyInt, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.MyInt"
        assert stringify_annotation(MyInt, "smart") == "~tests.test_util.test_util_typing.MyInt"
    else:
        assert stringify_annotation(MyInt, 'fully-qualified-except-typing') == "MyInt"
        assert stringify_annotation(MyInt, "smart") == "MyInt"


def test_stringify_type_hints_custom_class():
    assert stringify_annotation(MyClass1, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.MyClass1"
    assert stringify_annotation(MyClass1, "smart") == "~tests.test_util.test_util_typing.MyClass1"

    assert stringify_annotation(MyClass2, 'fully-qualified-except-typing') == "tests.test_util.test_util_typing.<MyClass2>"
    assert stringify_annotation(MyClass2, "smart") == "~tests.test_util.test_util_typing.<MyClass2>"


def test_stringify_type_hints_alias():
    MyStr = str
    MyTuple = Tuple[str, str]

    assert stringify_annotation(MyStr, 'fully-qualified-except-typing') == "str"
    assert stringify_annotation(MyStr, "smart") == "str"

    assert stringify_annotation(MyTuple) == "Tuple[str, str]"  # type: ignore[attr-defined]
    assert stringify_annotation(MyTuple, "smart") == "~typing.Tuple[str, str]"  # type: ignore[attr-defined]


def test_stringify_type_Literal():
    assert stringify_annotation(Literal[1, "2", "\r"], 'fully-qualified-except-typing') == "Literal[1, '2', '\\r']"
    assert stringify_annotation(Literal[1, "2", "\r"], "fully-qualified") == "typing.Literal[1, '2', '\\r']"
    assert stringify_annotation(Literal[1, "2", "\r"], "smart") == "~typing.Literal[1, '2', '\\r']"

    assert stringify_annotation(Literal[MyEnum.a], 'fully-qualified-except-typing') == 'Literal[tests.test_util.test_util_typing.MyEnum.a]'
    assert stringify_annotation(Literal[MyEnum.a], 'fully-qualified') == 'typing.Literal[tests.test_util.test_util_typing.MyEnum.a]'
    assert stringify_annotation(Literal[MyEnum.a], 'smart') == '~typing.Literal[MyEnum.a]'


@pytest.mark.skipif(sys.version_info[:2] <= (3, 9), reason='python 3.10+ is required.')
def test_stringify_type_union_operator():
    assert stringify_annotation(int | None) == "int | None"  # type: ignore[attr-defined]
    assert stringify_annotation(int | None, "smart") == "int | None"  # type: ignore[attr-defined]

    assert stringify_annotation(int | str) == "int | str"  # type: ignore[attr-defined]
    assert stringify_annotation(int | str, "smart") == "int | str"  # type: ignore[attr-defined]

    assert stringify_annotation(int | str | None) == "int | str | None"  # type: ignore[attr-defined]
    assert stringify_annotation(int | str | None, "smart") == "int | str | None"  # type: ignore[attr-defined]

    assert stringify_annotation(int | tuple[dict[str, int | None], list[int | str]] | None) == "int | tuple[dict[str, int | None], list[int | str]] | None"  # type: ignore[attr-defined]
    assert stringify_annotation(int | tuple[dict[str, int | None], list[int | str]] | None, "smart") == "int | tuple[dict[str, int | None], list[int | str]] | None"  # type: ignore[attr-defined]

    assert stringify_annotation(int | Struct) == "int | struct.Struct"  # type: ignore[attr-defined]
    assert stringify_annotation(int | Struct, "smart") == "int | ~struct.Struct"  # type: ignore[attr-defined]


def test_stringify_broken_type_hints():
    assert stringify_annotation(BrokenType, 'fully-qualified-except-typing') == 'tests.test_util.test_util_typing.BrokenType'
    assert stringify_annotation(BrokenType, "smart") == '~tests.test_util.test_util_typing.BrokenType'


def test_stringify_mock():
    with mock(['unknown']):
        import unknown
        assert stringify_annotation(unknown, 'fully-qualified-except-typing') == 'unknown'
        assert stringify_annotation(unknown.secret.Class, 'fully-qualified-except-typing') == 'unknown.secret.Class'
        assert stringify_annotation(unknown.secret.Class, "smart") == 'unknown.secret.Class'


def test_stringify_type_ForwardRef():
    assert stringify_annotation(ForwardRef("MyInt")) == "MyInt"
    assert stringify_annotation(ForwardRef("MyInt"), 'smart') == "MyInt"

    assert stringify_annotation(list[ForwardRef("MyInt")]) == "list[MyInt]"
    assert stringify_annotation(list[ForwardRef("MyInt")], 'smart') == "list[MyInt]"

    assert stringify_annotation(Tuple[dict[ForwardRef("MyInt"), str], list[List[int]]]) == "Tuple[dict[MyInt, str], list[List[int]]]"  # type: ignore[attr-defined]
    assert stringify_annotation(Tuple[dict[ForwardRef("MyInt"), str], list[List[int]]], 'fully-qualified-except-typing') == "Tuple[dict[MyInt, str], list[List[int]]]"  # type: ignore[attr-defined]
    assert stringify_annotation(Tuple[dict[ForwardRef("MyInt"), str], list[List[int]]], 'smart') == "~typing.Tuple[dict[MyInt, str], list[~typing.List[int]]]"  # type: ignore[attr-defined]
