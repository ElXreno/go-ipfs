%define _lto_cflags %{nil}

%bcond_with devel

%global goipath github.com/ipfs/%{name}
%global tag     v0.9.0-rc2

Name:           go-ipfs
Version:        0.9.0~rc.2
Release:        1%{?dist}
Summary:        IPFS implementation in Go

License:        MIT and Apache-2.0
URL:            https://ipfs.io
Source0:        https://github.com/ipfs/%{name}/releases/download/%{tag}/%{name}-source.tar.gz#/%{name}-%{version}.tar.gz
Source10:       ipfs.service
Source11:       ipfs-server.service
Source12:       ipfs-user.service
Source21:       ipfs.sysusers

# Allows to make dnf install ipfs
Provides:       ipfs

%gometa

# Temp
BuildRequires:  git

BuildRequires:  fuse-devel
BuildRequires:  pkgconfig(libssl)
BuildRequires:  pkgconfig(libcrypto)
Recommends:     fuse

%if 0%{?fedora} > 30
BuildRequires:  systemd-rpm-macros
%else
BuildRequires:  systemd-devel
%endif
%{?systemd_requires}

%description
IPFS is a global, versioned, peer-to-peer filesystem. It combines good ideas
from previous systems such as Git, BitTorrent, Kademlia, SFS, and the Web.
It is like a single BitTorrent swarm, exchanging git objects. IPFS provides
an interface as simple as the HTTP web, but with permanence built-in.
You can also mount the world at /ipfs.


%if %{with devel}
%package        devel
Summary:        IPFS implementation in Go (development files)
BuildArch:      noarch
 
%description    devel
This package contains the %{name} sources, which are needed as
dependency for building packages using %{name}.
%endif


%prep
%autosetup -c
# Pass -mod=vendor to `go list` and `go fmt` commands so it won't hit network
for f in cmd/ipfs/Rules.mk \
         coverage/Rules.mk \
         plugin/loader/Rules.mk \
         mk/golang.mk \
         ; do
    sed \
        -e 's/\($(GOCC) list\) /\1 -mod=vendor /g' \
        -e 's/\(go fmt\) /\1 -mod=vendor /g' \
        -e 's/\($(GOCC) build\) /\1 -mod=vendor /g' \
        -i $f
done


%build
# We can't use %%goprep, so set up environment manually
mkdir -p _build/src/github.com/ipfs
ln -sr $(pwd) _build/src/github.com/ipfs/%{name}
export GOPATH=$(pwd)/_build:%{gopath}

export CGO_ENABLED=1
export CGO_CFLAGS="%{__global_cflags}"
export CGO_CXXFLAGS="%{__global_cxxflags}"
export CGO_CPPFLAGS="$CGO_CXXFLAGS"
export CGO_LDFLAGS="%{__global_ldflags}"

make build GOTAGS=openssl


%install
#make install
install -Dm755 cmd/ipfs/ipfs -t %{buildroot}%{_bindir}

%if %{with devel}
%goinstall
%endif

mkdir -p %{buildroot}%{_sharedstatedir}/ipfs

install -D %SOURCE10 %{buildroot}%{_unitdir}/ipfs.service
install -D %SOURCE11 %{buildroot}%{_unitdir}/ipfs-server.service
install -D %SOURCE12 %{buildroot}%{_userunitdir}/ipfs.service
install -D %SOURCE21 %{buildroot}%{_sysusersdir}/ipfs.conf

install -D misc/completion/ipfs-completion.bash %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}


%pre
%sysusers_create_package ipfs %SOURCE21

%post
%systemd_post ipfs.service
%systemd_post ipfs-server.service
%systemd_user_post ipfs.service

%preun
%systemd_preun ipfs.service
%systemd_preun ipfs-server.service
%systemd_user_preun ipfs.service

%postun
%systemd_postun_with_restart ipfs.service
%systemd_postun_with_restart ipfs-server.service
%systemd_user_postun_with_restart ipfs.service


%files
%license LICENSE LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md
%{_bindir}/ipfs
%{_sysconfdir}/bash_completion.d/%{name}
%{_unitdir}/ipfs.service
%{_unitdir}/ipfs-server.service
%{_userunitdir}/ipfs.service
%{_sysusersdir}/ipfs.conf
%dir %attr(775,ipfs,ipfs) %{_sharedstatedir}/ipfs


%if %{with devel}
%files devel -f devel.file-list
%license LICENSE LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md
%endif


%changelog
* Fri May 28 2021 ElXreno <elxreno@gmail.com> - 0.9.0~rc.2-1
- Update to version 0.9.0-rc2

* Fri May 14 2021 ElXreno <elxreno@gmail.com> - 0.9.0~rc.1-1
- Update to version 0.9.0-rc1

* Fri Feb 19 2021 ElXreno <elxreno@gmail.com> - 0.8.0-1
- Update to version 0.8.0

* Fri Jan 29 2021 ElXreno <elxreno@gmail.com> - 0.8.0~rc.2-1
- Update to version 0.8.0-rc2

* Wed Jan 13 21:31:04 +03 2021 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-6
- Provides: ipfs

* Wed Jan 13 21:29:47 +03 2021 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-5
- Remove ipfs@.service, add user service

* Sun Jan 10 11:52:53 +03 2021 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-4
- Drop MemoryDenyWriteExecute=true from services

* Sun Jan 10 09:31:46 +03 2021 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-3
- Add user systemd service, hardening services

* Sat Dec 12 08:16:48 +03 2020 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-2
- rebuilt

* Thu Dec 10 10:10:12 +03 2020 ElXreno <elxreno@gmail.com> - 0.8.0~rc.1-1
- Update to version 0.8.0-rc1

* Fri Nov 20 22:19:38 +03 2020 ElXreno <elxreno@gmail.com> - 0.7.0-4
- Add bash completion file

* Sat Sep 26 2020 ElXreno <elxreno@gmail.com> - 0.7.0-3
- Fix offline build

* Sat Sep 26 2020 ElXreno <elxreno@gmail.com> - 0.7.0-2
- Disable LTO

* Wed Sep 23 2020 ElXreno <elxreno@gmail.com> - 0.7.0-1
- Update to version 0.7.0

* Fri Sep 11 2020 ElXreno <elxreno@gmail.com> - 0.7.0~rc.2-1
- Update to version 0.7.0-rc2

* Fri Aug 28 2020 ElXreno <elxreno@gmail.com> - 0.7.0~rc.1-1
- Update to version 0.7.0-rc1

* Sat Jun 20 2020 ElXreno <elxreno@gmail.com> - 0.6.0-1
- Updated to version 0.6.0

* Wed Jun 17 2020 ElXreno <elxreno@gmail.com> - 0.6.0~rc.7-1
- Updated to version 0.6.0-rc7

* Tue Jun 02 2020 ElXreno <elxreno@gmail.com> - 0.6.0~rc.1-1
- Update to version 0.6.0-rc.1

* Tue May 19 2020 gasinvein <gasinvein@gmail.com> - 0.5.1-0.2
- Add systemd units

* Mon May 18 2020 gasinvein <gasinvein@gmail.com> - 0.5.1-0.1
- Initial package
