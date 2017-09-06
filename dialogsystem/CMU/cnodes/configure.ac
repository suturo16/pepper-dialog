
#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([dialogsystem], [0.0.0], [fkenghag@uni-bremen.de])
AC_CONFIG_HEADERS([include/config.h])
AM_INIT_AUTOMAKE([no-define foreign])
AC_CONFIG_MACRO_DIR([m4])

# Checks for standard programs.
AC_PROG_CXX
AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_MAKE_SET
AC_CHECK_PROG(HAVE_PKGCONFIG, pkg-config, yes, no)
AC_CHECK_PROG(HAVE_DOXYGEN, doxygen, yes, no)
AM_CONDITIONAL(BUILD_DOXYGEN, test "x$HAVE_DOXYGEN" = "xyes")

#libtool tests
LT_INIT


#Checks for  python
AC_ARG_WITH(python,
	AS_HELP_STRING([--with-python],
                 [Enable Python extension, built with swig, enabled by default]))
if test "x${with_python}" != "xno"; then
  AM_PATH_PYTHON(2.6, [], [AC_MSG_ERROR([python not found])])
  AX_PYTHON_DEVEL()
  AX_PKG_SWIG(2.0, [], [AC_MSG_ERROR([swig not found])])
fi

AC_SUBST([PYTHON_CPPFLAGS])
CPPFLAGS="$CPPFLAGS $PYTHON_CPPFLAGS"
AM_CONDITIONAL(BUILD_SWIG, test "x$SWIG" != "x")

#Checks for  gst
GST_MAJORMINOR=1.0
PKG_CHECK_MODULES(GStreamer, [gstreamer-$GST_MAJORMINOR >= 1.0
		       gstreamer-base-$GST_MAJORMINOR >= 1.0
		       gstreamer-plugins-base-$GST_MAJORMINOR >= 1.0],
                  HAVE_GST=yes, HAVE_GST=no)
# Don't build GStreamer when cross-compiling
AM_CONDITIONAL(BUILD_GST, test x$cross_compiling != xyes && test "x$HAVE_GST" = "xyes")
GST_CFLAGS="$GStreamer_CFLAGS $GStreamer_ERROR"
GST_LIBS="$GStreamer_LIBS"
CPPFLAGS="$CPPFLAGS $GST_CFLAGS"
AC_SUBST(GST_MAJORMINOR)
AC_SUBST(GST_CFLAGS)
AC_SUBST(GST_LIBS)

dnl set the plugindir where plugins should be installed
if test "x${prefix}" = "x$HOME"; then
  plugindir="$HOME/.gstreamer-$GST_MAJORMINOR/plugins"
else
  plugindir="\$(libdir)/gstreamer-$GST_MAJORMINOR"
fi
AC_SUBST(plugindir)

dnl set proper LDFLAGS for plugins
GST_PLUGIN_LDFLAGS='-module -avoid-version -export-symbols-regex [_]*\(gst_\|Gst\|GST_\).*'
AC_SUBST(GST_PLUGIN_LDFLAGS)

#Checks for sphinxbase

AC_ARG_WITH(sphinxbase,
	AS_HELP_STRING([--with-sphinxbase=DIRECTORY],
			[Look for SphinxBase installation in DIRECTORY.  If this is 'auto',
			 the system-wide installation will be used.]),
			 sphinxbase=$withval)



# Check for SphinxBase in parent directories

if test x$sphinxbase = x; then
   dn=`dirname $0`
   case "$dn" in
	.)
	sbdir="`pwd`/.."
	;;
	[\\/]* | ?:[\\/]*)
	sbdir="$dn/.."
	;;
	*)
	sbdir="`pwd`/$dn/.."
	;;
   esac
   # Look for sphinxbase in the parent directory
   for sb in "$sbdir/sphinxbase" \
	  "$sbdir/sphinxbase"*; do
       AC_MSG_CHECKING([for sphinxbase in $sb])
       if test -f "$sb/src/libsphinxbase/libsphinxbase.la"; then
          sphinxbase="$sb"
	  AC_MSG_RESULT(yes)
	  break
       else
	  AC_MSG_RESULT(no)
       fi
   done
fi


# Check for system SphinxBase if none was passed to us
# Also allow --with-sphinxbase=auto to use system one explicitly

if test x$sphinxbase = x || test x$sphinxbase = xauto; then
   sphinxbase=

   if test "x$HAVE_PKGCONFIG" = "xno"; then
      SPHINXBASE_CFLAGS = "-I/usr/include/sphinxbase -I/usr/local/include/sphinxbase"
      SPHINXBASE_LIBS = "-lsphinxbase"
      SPHINXBASE_PREFIX="/usr/local"
   else
      PKG_CHECK_MODULES(SPHINXBASE, [sphinxbase],,[
      AC_MSG_FAILURE(dnl
[SphinxBase was not found on your system.
Make sure that you have installed it and that the
PKG_CONFIG_PATH environment variable is set correctly, if
it was installed in a non-standard prefix.])])
      SPHINXBASE_PREFIX=`pkg-config --variable=prefix sphinxbase`
   fi
   
   LIBS="$LIBS $SPHINXBASE_LIBS"
   CPPFLAGS="$CPPFLAGS $SPHINXBASE_CFLAGS"
   SPHINXBASE_SWIG="$SPHINXBASE_PREFIX/share/sphinxbase/swig"
   AC_CHECK_HEADER(sphinx_config.h,,[AC_MSG_FAILURE([SphinxBase was not found on your system.])])
else
   LIBS="$LIBS -lsphinxbase"
   LDFLAGS="$LDFLAGS -L$sphinxbase/lib -L$sphinxbase/src/libsphinxad -L$sphinxbase/src/libsphinxbase"
   CPPFLAGS="$CPPFLAGS -I$sphinxbase/include -I$sphinxbase/include/sphinxbase"
   SPHINXBASE_SWIG="$sphinxbase/swig"
fi

AC_SUBST(SPHINXBASE_SWIG)


# Checks for libraries.
# FIXME: Replace `main' with a function in `-lm':
AC_CHECK_LIB([m], [main])
# FIXME: Replace `main' with a function in `-lsphinxad':
AC_CHECK_LIB([sphinxad], [main])
# FIXME: Replace `main' with a function in `-lsphinxbase':
AC_CHECK_LIB([sphinxbase], [main])
# FIXME: Replace `main' with a function in `-lpthread':
AC_CHECK_LIB([pthread], [pthread_create])
# FIXME: Replace `main' with a function in `-lboost_system':
AC_CHECK_LIB([boost_system], [main])
# FIXME: Replace `main' with a function in `-lgstreamer-1.0 ':
AC_CHECK_LIB([gstreamer-1.0 ], [gst_element_set_state])
# FIXME: Replace `main' with a function in `-lgobject-2.0 ':
AC_CHECK_LIB([gobject-2.0], [g_object_set])
# FIXME: Replace `main' with a function in `-lglib-2.0 ':
AC_CHECK_LIB([glib-2.0], [g_main_loop_quit])
# FIXME: Replace `main' with a function in `-lboost_thread':
AC_CHECK_LIB([boost_thread], [main])
# FIXME: Replace `main' with a function in `-lxmlrpc_client':
AC_CHECK_LIB([xmlrpc_client], [main])
# FIXME: Replace `main' with a function in `-lxmlrpc':
AC_CHECK_LIB([xmlrpc], [main])
# FIXME: Replace `main' with a function in `-lxmlrpc_util':
AC_CHECK_LIB([xmlrpc_util], [main])

# Checks for header files.

AC_CHECK_HEADERS([fcntl.h float.h limits.h stdlib.h gst.h string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([memset select sqrt strchr strrchr])

AC_CONFIG_FILES([pocketsphinx.pc
		Makefile
		include/Makefile
		src/Makefile
		swig/Makefile
		swig/python/Makefile
		swig/python/test/Makefile
		src/libpocketsphinx/Makefile
		src/programs/Makefile
		src/gst-plugin/Makefile
		doc/Makefile
		doc/doxyfile
		model/Makefile
		test/Makefile
		test/testfuncs.sh
		test/unit/Makefile
		test/regression/Makefile])
AC_OUTPUT
