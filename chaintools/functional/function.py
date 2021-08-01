from __future__ import annotations
from typing import Optional, Union, Callable, Iterable, Generator, Any, List, Tuple
from inspect import Signature, signature

from chaintools.core import (
    Chainable,
    Argument,
    Annotation,
)


class Function(metaclass=Chainable):
    """ Chainable Function
    """
    TYPE = Callable[[Argument.TYPE], Any]

    def __init__(self, function: Optional[Union[Callable, Iterable[Callable]]] = None):
        self.__funcs__: List[Function.TYPE] = []
        if function is None:
            pass
        elif callable(function):
            self.__funcs__.append(function)
        elif isinstance(function, Iterable):
            self.__funcs__.extend(function)
        else:
            raise TypeError(f'{function} is not a callable or list of callables')

    def __str__(self) \
            -> str:
        annotations = self.annotations

        types: List[str] = []
        for annotation in annotations:
            if len(types) > 0:
                if types[-1] != annotation.param_type:
                    types[-1] = f'{types[-1]}({annotation.param_type})'
            else:
                types.append(annotation.param_type)

            types.append(annotation.return_type)

        return f'{self.__class__.__name__}({" -> ".join(types)})'

    def __call__(self, *args, **kwargs) \
            -> Any:
        args = Argument(*args, **kwargs)
        for function in self.__funcs__:
            args = args.evaluate(function)

        return args.value

    def __rshift__(self, function: Function.TYPE):
        self.__funcs__.append(function)
        return self

    def __lshift__(self, item: Any) \
            -> Any:
        result = self.__call__(item)
        return result

    @property
    def signature(self) \
            -> Tuple[Signature, ...]:
        return tuple(map(signature, self.__funcs__))

    @property
    def annotations(self) \
            -> Tuple[Annotation, ...]:
        return tuple(map(Annotation, map(signature, self.__funcs__)))

    def map(self, items: Iterable[Any]) \
            -> Generator[Any, None, None]:
        for function in self.__funcs__:
            items = map(function, items)

        return items
    
    def filter(self, items: Iterable[Any]) \
            -> Generator[Any, None, None]:
        for function in self.__funcs__:
            items = filter(function, items)

        return items

    @staticmethod
    def spread():
        """ Spread Function
        """
        def _wrapper(args: Optional[Argument.ARGS_TYPE]) \
                -> Argument:
            return Argument(*args)
            
        return _wrapper
