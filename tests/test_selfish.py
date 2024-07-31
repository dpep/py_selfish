#!/usr/bin/env python

import inspect
import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from selfish import selfish


@selfish
class Foo():
    def itself(): return self

    @classmethod
    def itsclass(): return self

    @staticmethod
    def static(): return globals().get('self')

# test with args

# for test_globals()
global_self = 123

# for test_locals()
local_self = 123


class SelfishTest(unittest.TestCase):

    def test_basics(self):
        foo = Foo()
        self.assertEqual(foo, foo.itself())
        self.assertEqual(Foo, foo.itsclass())
        self.assertEqual(Foo, Foo.itsclass())
        self.assertEqual(None, foo.static())
        self.assertEqual(None, Foo.static())


    def test_name(fn_self):
        @selfish(name='this')
        class Foo():
            def itself():
                with fn_self.assertRaises(NameError):
                    # undefined
                    self

                return this

        foo = Foo()
        fn_self.assertEqual(foo, foo.itself())


    def test_instance_var(fn_self):
        @selfish
        class Foo():
            def __init__(val): self.val = val
            def get(): return self.val

        fn_self.assertEqual(123, Foo(123).get())


    def test_args(fn_self):
        @selfish
        class Foo():
            def itself(arg): return arg

            @classmethod
            def itsclass(arg): return arg

            @staticmethod
            def static(arg): return arg

        fn_self.assertEqual(123, Foo().itself(123))
        fn_self.assertEqual(123, Foo().itsclass(123))
        fn_self.assertEqual(123, Foo.itsclass(123))
        fn_self.assertEqual(123, Foo().static(123))
        fn_self.assertEqual(123, Foo.static(123))


    def test_class_inheritence(fn_self):
        @selfish
        class Foo(dict):
            def double():
                return [ x * 2 for x in self.values() ]

        # inherited methods are unaffected
        fn_self.assertEqual(1, len(Foo({ 'a' : 1 })))
        fn_self.assertEqual([ 1 ], list(Foo({ 'a' : 1 }).values()))

        # new methods are selfish
        fn_self.assertEqual([ 2 ], Foo({ 'a' : 1 }).double())


    def test_closure(self):
        with self.assertRaises(NameError):
            @selfish
            class Nope():
                # 'self' already bound from test_closure()
                def itself(): return self


    def test_wrapper(self):
        # ensure selfish methods are wrapped up properly

        self.assertTrue(inspect.isclass(Foo))
        self.assertEqual('Foo', Foo.__name__)

        self.assertIn(
            'function Foo.itself',
            str(Foo.itself)
        )
        self.assertEqual('itself', Foo.itself.__name__)


    def test_globals(fn_self):
        fn_self.assertEqual(123, global_self)
        fn_self.assertNotIn('global_self', locals())

        @selfish(name='global_self')
        class Change():
            def do(val):
                globals()['global_self'] = val

        Change().do(789)

        # change to globals should persist
        fn_self.assertEqual(789, global_self)


    def test_locals(fn_self):
        local_self = 111

        fn_self.assertIn('local_self', locals())
        fn_self.assertIn('local_self', globals())
        fn_self.assertNotEqual(
            locals()['local_self'],
            globals()['local_self']
        )

        @selfish
        class Change():
            def do(val):
                # because it's not statically referenced, 'local_self'
                # in test_locals() isn't actually brought into
                # scope.  only the global one exists and it's been
                # overwritten by selfish

                fn_self.assertNotIn('local_self', locals())
                globals()['local_self'] = val

        Change().do(999)

        # local value should not have changed
        fn_self.assertEqual(111, local_self)

        # but the global one did
        fn_self.assertEqual(999, globals()['local_self'])


    def test_input(self):
        # can only make classes selfish

        with self.assertRaises(ValueError):
            def foo(): pass
            selfish(foo)

        with self.assertRaises(ValueError):
            selfish(lambda: 123)


if __name__ == '__main__':
    unittest.main()
