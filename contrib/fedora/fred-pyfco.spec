%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define debug_package %{nil}

Summary: Library contains python code to interact FRED corba backend
Name: fred-pyfco
Version: %{our_version}
Release: %{?our_release}%{!?our_release:1}%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPLv3+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: CZ.NIC <fred@nic.cz>
Url: https://fred.nic.cz/

%package -n python3-fred-pyfco
Summary: Library contains python3 code to interact FRED corba backend
BuildRequires: python3 python3-setuptools
Requires: python3 python3-six python3-pytz python3-omniORB python3-fred-idl

%package -n python2-fred-pyfco
Summary: Library contains python2 code to interact FRED corba backend
BuildRequires: python2 python2-setuptools
Requires: python2 python2-six python2-pytz python2-omniORB python2-fred-idl

%description -n python3-fred-pyfco
Library contains python3 code interacting with FRED corba backend

%description -n python2-fred-pyfco
Library contains python2 code interacting with FRED corba backend

%description
Library contains python code interacting with FRED corba backend

%prep
%setup -n %{name}-%{version}

%install
/usr/bin/python2 setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES_P2 --prefix=/usr
/usr/bin/python3 setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES_P3 --prefix=/usr

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python3-fred-pyfco -f INSTALLED_FILES_P3
%defattr(-,root,root)

%files -n python2-fred-pyfco -f INSTALLED_FILES_P2
%defattr(-,root,root)
