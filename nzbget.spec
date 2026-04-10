Name:           nzbget
Version:        26.1
Release:        1%{?dist}
Summary:        An Efficient Usenet Downloader
License:        GPL-2.0-or-later
URL:            https://github.com/nzbgetcom/nzbget
Source0:        https://github.com/nzbgetcom/nzbget/archive/refs/tags/v%{version}.tar.gz#/nzbget-%{version}.tar.gz
Source1:        nzbget.systemd
Source2:        nzbget.xml
Source3:        nzbget-secure.xml

# Useful NZBGetScripts
# pulled from https://github.com/clinton-hall/GetScripts/
Source4:        ResetDateTime.py
Source5:        DeleteSamples.py
Source6:        Flatten.py
Source7:        PasswordList.py
# This scan-script reads category information from nzb-file 
# (if it's present in meta-tag) and sets the category for nzb-file
# when adding to queue.
# Author: Hugbug (src: https://forum.nzbget.net/viewtopic.php?f=8&t=2999)
Source8:        MetaCategory.py

Source9:        Completion.py

Source10:       https://github.com/nzbgetcom/rapidyenc/archive/refs/tags/v1.1.1-20260217.tar.gz#/rapidyenc-1.1.1-20260217.tar.gz
Source11:       https://github.com/nzbgetcom/par2cmdline-turbo/archive/refs/tags/v1.4.0-20260323.tar.gz#/par2cmdline-turbo-1.4.0-20260323.tar.gz
Source12:       https://github.com/boostorg/boost/releases/download/boost-1.84.0/boost-1.84.0.tar.xz
Source13:       nzbget.sysusers

Patch0:         0001-local-vendor-sources.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  libxml2-devel
BuildRequires:  openssl-devel
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel
%if 0%{?fedora} >= 30 || 0%{?rhel} >= 8
BuildRequires:  systemd-rpm-macros
%endif

%if 0%{?rhel} == 8
BuildRequires:  perl-interpreter
Provides:       bundled(boost) = 1.84.0
%else
BuildRequires:  boost-devel
%endif

Provides:       bundled(rapidyenc) = 1.1.1-20260217
Provides:       bundled(par2cmdline-turbo) = 1.4.0-20260323

Requires(pre):  shadow-utils
Requires:       firewalld-filesystem

%description
NZBGet is a cross-platform binary newsgrabber for nzb files, written in C++.
It supports client/server mode, automatic par-check/-repair and web-interface.
NZBGet requires low system resources and runs great on routers,
NAS-devices and media players.

%prep
%autosetup -p1 -n %{name}-%{version}

mkdir -p vendor

tar -xf %{SOURCE10} -C vendor
mv vendor/rapidyenc-* vendor/rapidyenc

tar -xf %{SOURCE11} -C vendor
mv vendor/par2cmdline-turbo-* vendor/par2cmdline-turbo

%if 0%{?rhel} == 8
tar -xf %{SOURCE12} -C vendor
mv vendor/boost-* vendor/boost
%endif

# fix-up python references; this effectively changes
# #!/usr/bin/env python
#  to:
# #!/usr/bin/python3
[ -d scripts ] && find scripts -type f -name '*.py' -exec \
   sed -i -e 's|#!.*env python[23]\?$|#!/usr/bin/python3|g' {} \;
for file in %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE8} %{SOURCE9}; do
   sed -i -e 's|#!.*env python[23]\?$|#!/usr/bin/python3|g' $file
done

%build
%if 0%{?rhel} == 8
%cmake \
   -DENABLE_TESTS=OFF \
   -DRAPIDYENC_SOURCE_DIR=%{_builddir}/%{name}-%{version}/vendor/rapidyenc \
   -DPAR2_TURBO_SOURCE_DIR=%{_builddir}/%{name}-%{version}/vendor/par2cmdline-turbo \
   -DBOOST_SOURCE_DIR_LOCAL=%{_builddir}/%{name}-%{version}/vendor/boost
%else
%cmake \
   -DENABLE_TESTS=OFF \
   -DRAPIDYENC_SOURCE_DIR=%{_builddir}/%{name}-%{version}/vendor/rapidyenc \
   -DPAR2_TURBO_SOURCE_DIR=%{_builddir}/%{name}-%{version}/vendor/par2cmdline-turbo
%endif
%cmake_build

%install
%cmake_install

# Create a global configuration file from sample already
install -p -D -m 644 %{SOURCE1} \
                %{buildroot}/%{_unitdir}/nzbget.service
install -p -D -m 644 %{SOURCE13} \
                %{buildroot}/%{_sysusersdir}/nzbget.conf
install -p -D -m 660 %{buildroot}%{_datadir}/%{name}/nzbget.conf \
                %{buildroot}/%{_sysconfdir}/nzbget.conf

sed -i -e 's|^MainDir=.*|MainDir=%{_sharedstatedir}/%{name}|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^DestDir=.*|DestDir=${MainDir}/downloads|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^InterDir=.*|InterDir=${MainDir}/inter|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^NzbDir=.*|NzbDir=${MainDir}/nzb|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^QueueDir=.*|QueueDir=${MainDir}/queue|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^TempDir=.*|TempDir=${MainDir}/tmp|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^WebDir=.*|WebDir=%{_datadir}/%{name}/webui|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^ScriptDir=.*|ScriptDir=%{_datadir}/%{name}/scripts|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^LogFile=.*|LogFile=%{_localstatedir}/log/%{name}/nzbget.log|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^ConfigTemplate=.*|ConfigTemplate=%{_datadir}/%{name}/nzbget.conf|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^WriteLog=.*|WriteLog=rotate|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^UnrarCmd=.*|UnrarCmd=%{_bindir}/unrar|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf
sed -i -e 's|^SevenZipCmd=.*|SevenZipCmd=%{_bindir}/7za|g' \
   %{buildroot}/%{_datadir}/%{name}/nzbget.conf \
   %{buildroot}/%{_sysconfdir}/nzbget.conf

# remove old RC Script
rm -f %{buildroot}/%{_sbindir}/%{name}d

mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}/nzb
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}/queue
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}/tmp
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}/inter
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}/downloads

# Logging
mkdir -p %{buildroot}/var/log/%{name}

# Scripts
mkdir -p %{buildroot}/%{_datadir}/%{name}/scripts
install -p -m 755 scripts/EMail.py \
   %{buildroot}/%{_datadir}/%{name}/scripts/EMail.py
install -p -m 755 scripts/Logger.py \
   %{buildroot}/%{_datadir}/%{name}/scripts/Logger.py

# Extra Useful Scripts
install -p -D -m 755 %{SOURCE4} \
   %{buildroot}/%{_datadir}/%{name}/scripts/ResetDateTime.py
install -p -D -m 755 %{SOURCE5} \
   %{buildroot}/%{_datadir}/%{name}/scripts/DeleteSamples.py
install -p -D -m 755 %{SOURCE6} \
   %{buildroot}/%{_datadir}/%{name}/scripts/Flatten.py
install -p -D -m 755 %{SOURCE7} \
   %{buildroot}/%{_datadir}/%{name}/scripts/PasswordList.py
install -p -D -m 755 %{SOURCE8} \
   %{buildroot}/%{_datadir}/%{name}/scripts/MetaCategory.py
install -p -D -m 755 %{SOURCE9} \
   %{buildroot}/%{_datadir}/%{name}/scripts/Completion.py

# Firewalld Support
install -D -m 644 %{SOURCE2} \
                %{buildroot}%{_prefix}/lib/firewalld/services/nzbget.xml
install -D -m 644 %{SOURCE3} \
                %{buildroot}%{_prefix}/lib/firewalld/services/nzbget-secure.xml

%pre
%sysusers_create_compat %{SOURCE13}

%post
%systemd_post nzbget.service

%preun
%systemd_preun nzbget.service

%postun
%systemd_postun_with_restart nzbget.service

%files
%doc %{_datadir}/%{name}/doc/ChangeLog.md
%license %{_datadir}/%{name}/doc/COPYING

# Passwords are stored in this file; intentionally made as having no rwx
# permissions for 'other' users
%attr(0660,nzbget,root) %config(noreplace) %{_sysconfdir}/nzbget.conf
%{_prefix}/lib/firewalld/services/nzbget.xml
%{_prefix}/lib/firewalld/services/nzbget-secure.xml

%attr(0755,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}
%attr(0775,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}/nzb
%attr(0755,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}/inter
%attr(0755,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}/queue
%attr(0755,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}/tmp
%attr(0775,nzbget,nzbget) %dir %{_sharedstatedir}/%{name}/downloads
# 770 because invalid usernames and passwords are printed in clear text in
# this log file
%attr(0770,nzbget,root) %dir /var/log/%{name}

%{_bindir}/%{name}
%{_unitdir}/nzbget.service
%{_sysusersdir}/nzbget.conf
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/nzbget.conf
%{_datadir}/%{name}/scripts
%{_datadir}/%{name}/webui

%changelog
* Fri Apr 10 2026 Alexander Brügmann <mail@abruegmann.eu> - 26.1-1
- update to current upstream release
- switch to cmake build system
- vendor build-only sources locally for networkless builds

* Sun Sep 04 2022 Chris Caron <lead2gold@gmail.com> - 21.1-3
- added 6 useful scripts as part of packaging

* Sun Sep 04 2022 Chris Caron <lead2gold@gmail.com> - 21.1-2
- Updated NZBGet webui Configuration Path

* Tue Aug 30 2022 Chris Caron <lead2gold@gmail.com> - 21.1-1
- Updated to NZBGet v21.1

* Sun Sep 06 2020 Chris Caron <lead2gold@gmail.com> - 21.0-2
- Updated to include firewalld configuration

* Fri May 03 2019 Chris Caron <lead2gold@gmail.com> - 21.0-1
- Initial install of NZBget v21.0
