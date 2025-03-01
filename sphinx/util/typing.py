"""The composite types for Sphinx."""

from __future__ import annotations

import sys
import types
import typing
from collections.abc import Sequence
from contextvars import Context, ContextVar, Token
from struct import Struct
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ForwardRef,
    TypedDict,
    TypeVar,
    Union,
)

from docutils import nodes
from docutils.parsers.rst.states import Inliner

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Final, Literal, Protocol

    from typing_extensions import TypeAlias, TypeIs

    from sphinx.application import Sphinx

    _RestifyMode: TypeAlias = Literal[
        'fully-qualified-except-typing',
        'smart',
    ]
    _StringifyMode: TypeAlias = Literal[
        'fully-qualified-except-typing',
        'fully-qualified',
        'smart',
    ]

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = None

# classes that have an incorrect .__module__ attribute
_INVALID_BUILTIN_CLASSES: Final[Mapping[object, str]] = {
    Context: 'contextvars.Context',  # Context.__module__ == '_contextvars'
    ContextVar: 'contextvars.ContextVar',  # ContextVar.__module__ == '_contextvars'
    Token: 'contextvars.Token',  # Token.__module__ == '_contextvars'
    Struct: 'struct.Struct',  # Struct.__module__ == '_struct'
    # types in 'types' with <type>.__module__ == 'builtins':
    types.AsyncGeneratorType: 'types.AsyncGeneratorType',
    types.BuiltinFunctionType: 'types.BuiltinFunctionType',
    types.BuiltinMethodType: 'types.BuiltinMethodType',
    types.CellType: 'types.CellType',
    types.ClassMethodDescriptorType: 'types.ClassMethodDescriptorType',
    types.CodeType: 'types.CodeType',
    types.CoroutineType: 'types.CoroutineType',
    types.FrameType: 'types.FrameType',
    types.FunctionType: 'types.FunctionType',
    types.GeneratorType: 'types.GeneratorType',
    types.GetSetDescriptorType: 'types.GetSetDescriptorType',
    types.LambdaType: 'types.LambdaType',
    types.MappingProxyType: 'types.MappingProxyType',
    types.MemberDescriptorType: 'types.MemberDescriptorType',
    types.MethodDescriptorType: 'types.MethodDescriptorType',
    types.MethodType: 'types.MethodType',
    types.MethodWrapperType: 'types.MethodWrapperType',
    types.ModuleType: 'types.ModuleType',
    types.TracebackType: 'types.TracebackType',
    types.WrapperDescriptorType: 'types.WrapperDescriptorType',
}


def is_invalid_builtin_class(obj: Any) -> bool:
    """Check *obj* is an invalid built-in class."""
    try:
        return obj in _INVALID_BUILTIN_CLASSES
    except TypeError:  # unhashable type
        return False


# Text like nodes which are initialized with text and rawsource
TextlikeNode = Union[nodes.Text, nodes.TextElement]

# type of None
NoneType = type(None)

# path matcher
PathMatcher = Callable[[str], bool]

# common role functions
if TYPE_CHECKING:
    class RoleFunction(Protocol):
        def __call__(
            self,
            name: str,
            rawtext: str,
            text: str,
            lineno: int,
            inliner: Inliner,
            /,
            options: dict[str, Any] | None = None,
            content: Sequence[str] = (),
        ) -> tuple[list[nodes.Node], list[nodes.system_message]]:
            ...
else:
    RoleFunction = Callable[
        [str, str, str, int, Inliner, dict[str, Any], Sequence[str]],
        tuple[list[nodes.Node], list[nodes.system_message]],
    ]

# A option spec for directive
OptionSpec = dict[str, Callable[[str], Any]]

# title getter functions for enumerable nodes (see sphinx.domains.std)
TitleGetter = Callable[[nodes.Node], str]

# inventory data on memory
InventoryItem = tuple[
    str,  # project name
    str,  # project version
    str,  # URL
    str,  # display name
]
Inventory = dict[str, dict[str, InventoryItem]]


class ExtensionMetadata(TypedDict, total=False):
    """The metadata returned by an extension's ``setup()`` function.

    See :ref:`ext-metadata`.
    """

    version: str
    """The extension version (default: ``'unknown version'``)."""
    env_version: int
    """An integer that identifies the version of env data added by the extension."""
    parallel_read_safe: bool
    """Indicate whether parallel reading of source files is supported
    by the extension.
    """
    parallel_write_safe: bool
    """Indicate whether parallel writing of output files is supported
    by the extension (default: ``True``).
    """


if TYPE_CHECKING:
    _ExtensionSetupFunc = Callable[[Sphinx], ExtensionMetadata]


def get_type_hints(
    obj: Any,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a dictionary containing type hints for a function, method, module or class
    object.

    This is a simple wrapper of `typing.get_type_hints()` that does not raise an error on
    runtime.
    """
    from sphinx.util.inspect import safe_getattr  # lazy loading

    try:
        return typing.get_type_hints(obj, globalns, localns)
    except NameError:
        # Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
        return safe_getattr(obj, '__annotations__', {})
    except AttributeError:
        # Failed to evaluate ForwardRef (maybe not runtime checkable)
        return safe_getattr(obj, '__annotations__', {})
    except TypeError:
        # Invalid object is given. But try to get __annotations__ as a fallback.
        return safe_getattr(obj, '__annotations__', {})
    except KeyError:
        # a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
        return {}


def is_system_TypeVar(typ: Any) -> bool:
    """Check *typ* is system defined TypeVar."""
    modname = getattr(typ, '__module__', '')
    return modname == 'typing' and isinstance(typ, TypeVar)


def _is_annotated_form(obj: Any) -> TypeIs[Annotated[Any, ...]]:
    """Check if *obj* is an annotated type."""
    return typing.get_origin(obj) is Annotated or str(obj).startswith('typing.Annotated')


def _is_unpack_form(obj: Any) -> bool:
    """Check if the object is :class:`typing.Unpack` or equivalent."""
    if sys.version_info >= (3, 11):
        from typing import Unpack

        # typing_extensions.Unpack != typing.Unpack for 3.11, but we assume
        # that typing_extensions.Unpack should not be used in that case
        return typing.get_origin(obj) is Unpack

    # 3.9 and 3.10 require typing_extensions.Unpack
    origin = typing.get_origin(obj)
    return (
        getattr(origin, '__module__', None) == 'typing_extensions'
        and _typing_internal_name(origin) == 'Unpack'
    )


def _typing_internal_name(obj: Any) -> str | None:
    if sys.version_info[:2] >= (3, 10):
        return obj.__name__
    return getattr(obj, '_name', None)


def restify(cls: Any, mode: _RestifyMode = 'fully-qualified-except-typing') -> str:
    """Convert a type-like object to a reST reference.

    :param mode: Specify a method how annotations will be stringified.

                 'fully-qualified-except-typing'
                     Show the module name and qualified name of the annotation except
                     the "typing" module.
                 'smart'
                     Show the name of the annotation.
    """
    from sphinx.ext.autodoc.mock import ismock, ismockmodule  # lazy loading
    from sphinx.util import inspect  # lazy loading

    valid_modes = {'fully-qualified-except-typing', 'smart'}
    if mode not in valid_modes:
        valid = ', '.join(map(repr, sorted(valid_modes)))
        msg = f'mode must be one of {valid}; got {mode!r}'
        raise ValueError(msg)

    # things that are not types
    if cls in {None, NoneType}:
        return ':py:obj:`None`'
    if cls is Ellipsis:
        return '...'
    if isinstance(cls, str):
        return cls

    cls_module_is_typing = getattr(cls, '__module__', '') == 'typing'

    # If the mode is 'smart', we always use '~'.
    # If the mode is 'fully-qualified-except-typing',
    # we use '~' only for the objects in the ``typing`` module.
    module_prefix = '~' if mode == 'smart' or cls_module_is_typing else ''

    try:
        if ismockmodule(cls):
            return f':py:class:`{module_prefix}{cls.__name__}`'
        elif ismock(cls):
            return f':py:class:`{module_prefix}{cls.__module__}.{cls.__name__}`'
        elif is_invalid_builtin_class(cls):
            # The above predicate never raises TypeError but should not be
            # evaluated before determining whether *cls* is a mocked object
            # or not; instead of two try-except blocks, we keep it here.
            return f':py:class:`{module_prefix}{_INVALID_BUILTIN_CLASSES[cls]}`'
        elif _is_annotated_form(cls):
            args = restify(cls.__args__[0], mode)
            meta = ', '.join(map(repr, cls.__metadata__))
            if sys.version_info[:2] <= (3, 11):
                # Hardcoded to fix errors on Python 3.11 and earlier.
                return fr':py:class:`~typing.Annotated`\ [{args}, {meta}]'
            return (f':py:class:`{module_prefix}{cls.__module__}.{cls.__name__}`'
                    fr'\ [{args}, {meta}]')
        elif inspect.isNewType(cls):
            if sys.version_info[:2] >= (3, 10):
                # newtypes have correct module info since Python 3.10+
                return f':py:class:`{module_prefix}{cls.__module__}.{cls.__name__}`'
            return f':py:class:`{cls.__name__}`'
        elif UnionType and isinstance(cls, UnionType):
            # Union types (PEP 585) retain their definition order when they
            # are printed natively and ``None``-like types are kept as is.
            return ' | '.join(restify(a, mode) for a in cls.__args__)
        elif cls.__module__ in ('__builtin__', 'builtins'):
            if hasattr(cls, '__args__'):
                if not cls.__args__:  # Empty tuple, list, ...
                    return fr':py:class:`{cls.__name__}`\ [{cls.__args__!r}]'

                concatenated_args = ', '.join(restify(arg, mode) for arg in cls.__args__)
                return fr':py:class:`{cls.__name__}`\ [{concatenated_args}]'
            return f':py:class:`{cls.__name__}`'
        elif (inspect.isgenericalias(cls)
              and cls_module_is_typing
              and cls.__origin__ is Union):
            # *cls* is defined in ``typing``, and thus ``__args__`` must exist
            return ' | '.join(restify(a, mode) for a in cls.__args__)
        elif inspect.isgenericalias(cls):
            # A generic alias always has an __origin__, but it is difficult to
            # use a type guard on inspect.isgenericalias()
            # (ideally, we would use ``TypeIs`` introduced in Python 3.13).
            cls_name = _typing_internal_name(cls)

            if isinstance(cls.__origin__, typing._SpecialForm):
                # ClassVar; Concatenate; Final; Literal; Unpack; TypeGuard; TypeIs
                # Required/NotRequired
                text = restify(cls.__origin__, mode)
            elif cls_name:
                text = f':py:class:`{module_prefix}{cls.__module__}.{cls_name}`'
            else:
                text = restify(cls.__origin__, mode)

            __args__ = getattr(cls, '__args__', ())
            if not __args__:
                return text
            if all(map(is_system_TypeVar, __args__)):
                # Don't print the arguments; they're all system defined type variables.
                return text

            # Callable has special formatting
            if (
                (cls_module_is_typing and _typing_internal_name(cls) == 'Callable')
                or (cls.__module__ == 'collections.abc' and cls.__name__ == 'Callable')
            ):
                args = ', '.join(restify(a, mode) for a in __args__[:-1])
                returns = restify(__args__[-1], mode)
                return fr'{text}\ [[{args}], {returns}]'

            if cls_module_is_typing and _typing_internal_name(cls.__origin__) == 'Literal':
                args = ', '.join(_format_literal_arg_restify(a, mode=mode)
                                 for a in cls.__args__)
                return fr'{text}\ [{args}]'

            # generic representation of the parameters
            args = ', '.join(restify(a, mode) for a in __args__)
            return fr'{text}\ [{args}]'
        elif isinstance(cls, typing._SpecialForm):
            cls_name = _typing_internal_name(cls)
            return f':py:obj:`~{cls.__module__}.{cls_name}`'
        elif sys.version_info[:2] >= (3, 11) and cls is typing.Any:
            # handle bpo-46998
            return f':py:obj:`~{cls.__module__}.{cls.__name__}`'
        elif hasattr(cls, '__qualname__'):
            return f':py:class:`{module_prefix}{cls.__module__}.{cls.__qualname__}`'
        elif isinstance(cls, ForwardRef):
            return f':py:class:`{cls.__forward_arg__}`'
        else:
            # not a class (ex. TypeVar) but should have a __name__
            return f':py:obj:`{module_prefix}{cls.__module__}.{cls.__name__}`'
    except (AttributeError, TypeError):
        return inspect.object_description(cls)


def _format_literal_arg_restify(arg: Any, /, *, mode: str) -> str:
    from sphinx.util.inspect import isenumattribute  # lazy loading

    if isenumattribute(arg):
        enum_cls = arg.__class__
        if mode == 'smart' or enum_cls.__module__ == 'typing':
            # MyEnum.member
            return f':py:attr:`~{enum_cls.__module__}.{enum_cls.__qualname__}.{arg.name}`'
        # module.MyEnum.member
        return f':py:attr:`{enum_cls.__module__}.{enum_cls.__qualname__}.{arg.name}`'
    return repr(arg)


def stringify_annotation(
    annotation: Any,
    /,
    mode: _StringifyMode = 'fully-qualified-except-typing',
) -> str:
    """Stringify type annotation object.

    :param annotation: The annotation to stringified.
    :param mode: Specify a method how annotations will be stringified.

                 'fully-qualified-except-typing'
                     Show the module name and qualified name of the annotation except
                     the "typing" module.
                 'smart'
                     Show the name of the annotation.
                 'fully-qualified'
                     Show the module name and qualified name of the annotation.
    """
    from sphinx.ext.autodoc.mock import ismock, ismockmodule  # lazy loading
    from sphinx.util.inspect import isNewType  # lazy loading

    valid_modes = {'fully-qualified-except-typing', 'fully-qualified', 'smart'}
    if mode not in valid_modes:
        valid = ', '.join(map(repr, sorted(valid_modes)))
        msg = f'mode must be one of {valid}; got {mode!r}'
        raise ValueError(msg)

    # things that are not types
    if annotation in {None, NoneType}:
        return 'None'
    if annotation is Ellipsis:
        return '...'
    if isinstance(annotation, str):
        if annotation.startswith("'") and annotation.endswith("'"):
            # Might be a double Forward-ref'ed type.  Go unquoting.
            return annotation[1:-1]
        return annotation
    if not annotation:
        return repr(annotation)

    module_prefix = '~' if mode == 'smart' else ''

    # The values below must be strings if the objects are well-formed.
    annotation_qualname: str = getattr(annotation, '__qualname__', '')
    annotation_module: str = getattr(annotation, '__module__', '')
    annotation_name: str = getattr(annotation, '__name__', '')
    annotation_module_is_typing = annotation_module == 'typing'

    # Extract the annotation's base type by considering formattable cases
    if isinstance(annotation, TypeVar) and not _is_unpack_form(annotation):
        # typing_extensions.Unpack is incorrectly determined as a TypeVar
        if annotation_module_is_typing and mode in {'fully-qualified-except-typing', 'smart'}:
            return annotation_name
        return module_prefix + f'{annotation_module}.{annotation_name}'
    elif isNewType(annotation):
        if sys.version_info[:2] >= (3, 10):
            # newtypes have correct module info since Python 3.10+
            return module_prefix + f'{annotation_module}.{annotation_name}'
        return annotation_name
    elif ismockmodule(annotation):
        return module_prefix + annotation_name
    elif ismock(annotation):
        return module_prefix + f'{annotation_module}.{annotation_name}'
    elif is_invalid_builtin_class(annotation):
        return module_prefix + _INVALID_BUILTIN_CLASSES[annotation]
    elif _is_annotated_form(annotation):  # for py39+
        pass
    elif annotation_module == 'builtins' and annotation_qualname:
        args = getattr(annotation, '__args__', None)
        if args is None:
            return annotation_qualname

        # PEP 585 generic
        if not args:  # Empty tuple, list, ...
            return repr(annotation)

        concatenated_args = ', '.join(stringify_annotation(arg, mode) for arg in args)
        return f'{annotation_qualname}[{concatenated_args}]'
    else:
        # add other special cases that can be directly formatted
        pass

    module_prefix = f'{annotation_module}.'
    annotation_forward_arg: str | None = getattr(annotation, '__forward_arg__', None)
    if annotation_qualname or (annotation_module_is_typing and not annotation_forward_arg):
        if mode == 'smart':
            module_prefix = f'~{module_prefix}'
        if annotation_module_is_typing and mode == 'fully-qualified-except-typing':
            module_prefix = ''
    elif _is_unpack_form(annotation) and annotation_module == 'typing_extensions':
        module_prefix = '~' if mode == 'smart' else ''
    else:
        module_prefix = ''

    if annotation_module_is_typing:
        if annotation_forward_arg:
            # handle ForwardRefs
            qualname = annotation_forward_arg
        else:
            if internal_name := _typing_internal_name(annotation):
                qualname = internal_name
            elif annotation_qualname:
                qualname = annotation_qualname
            else:
                # in this case, we know that the annotation is a member
                # of ``typing`` and all of them define ``__origin__``
                qualname = stringify_annotation(
                    annotation.__origin__, 'fully-qualified-except-typing',
                ).replace('typing.', '')  # ex. Union
    elif annotation_qualname:
        qualname = annotation_qualname
    elif hasattr(annotation, '__origin__'):
        # instantiated generic provided by a user
        qualname = stringify_annotation(annotation.__origin__, mode)
    elif UnionType and isinstance(annotation, UnionType):  # types.UnionType (for py3.10+)
        qualname = 'types.UnionType'
    else:
        # we weren't able to extract the base type, appending arguments would
        # only make them appear twice
        return repr(annotation)

    # Process the generic arguments (if any).
    # They must be a list or a tuple, otherwise they are considered 'broken'.
    annotation_args = getattr(annotation, '__args__', ())
    if annotation_args and isinstance(annotation_args, (list, tuple)):
        if (
            qualname in {'Union', 'types.UnionType'}
            and all(getattr(a, '__origin__', ...) is typing.Literal for a in annotation_args)
        ):
            # special case to flatten a Union of Literals into a literal
            flattened_args = typing.Literal[annotation_args].__args__  # type: ignore[attr-defined]
            args = ', '.join(_format_literal_arg_stringify(a, mode=mode)
                             for a in flattened_args)
            return f'{module_prefix}Literal[{args}]'
        if qualname in {'Optional', 'Union', 'types.UnionType'}:
            return ' | '.join(stringify_annotation(a, mode) for a in annotation_args)
        elif qualname == 'Callable':
            args = ', '.join(stringify_annotation(a, mode) for a in annotation_args[:-1])
            returns = stringify_annotation(annotation_args[-1], mode)
            return f'{module_prefix}Callable[[{args}], {returns}]'
        elif qualname == 'Literal':
            args = ', '.join(_format_literal_arg_stringify(a, mode=mode)
                             for a in annotation_args)
            return f'{module_prefix}Literal[{args}]'
        elif _is_annotated_form(annotation):  # for py39+
            args = stringify_annotation(annotation_args[0], mode)
            meta = ', '.join(map(repr, annotation.__metadata__))
            if sys.version_info[:2] <= (3, 11):
                if mode == 'fully-qualified-except-typing':
                    return f'Annotated[{args}, {meta}]'
                module_prefix = module_prefix.replace('builtins', 'typing')
                return f'{module_prefix}Annotated[{args}, {meta}]'
            return f'{module_prefix}Annotated[{args}, {meta}]'
        elif all(is_system_TypeVar(a) for a in annotation_args):
            # Suppress arguments if all system defined TypeVars (ex. Dict[KT, VT])
            return module_prefix + qualname
        else:
            args = ', '.join(stringify_annotation(a, mode) for a in annotation_args)
            return f'{module_prefix}{qualname}[{args}]'

    return module_prefix + qualname


def _format_literal_arg_stringify(arg: Any, /, *, mode: str) -> str:
    from sphinx.util.inspect import isenumattribute  # lazy loading

    if isenumattribute(arg):
        enum_cls = arg.__class__
        if mode == 'smart' or enum_cls.__module__ == 'typing':
            # MyEnum.member
            return f'{enum_cls.__qualname__}.{arg.name}'
        # module.MyEnum.member
        return f'{enum_cls.__module__}.{enum_cls.__qualname__}.{arg.name}'
    return repr(arg)


# deprecated name -> (object to return, canonical path or empty string, removal version)
_DEPRECATED_OBJECTS: dict[str, tuple[Any, str, tuple[int, int]]] = {
    'stringify': (stringify_annotation, 'sphinx.util.typing.stringify_annotation', (8, 0)),
}


def __getattr__(name: str) -> Any:
    if name not in _DEPRECATED_OBJECTS:
        msg = f'module {__name__!r} has no attribute {name!r}'
        raise AttributeError(msg)

    from sphinx.deprecation import _deprecation_warning

    deprecated_object, canonical_name, remove = _DEPRECATED_OBJECTS[name]
    _deprecation_warning(__name__, name, canonical_name, remove=remove)
    return deprecated_object
