%bcond_with devel

%global goipath github.com/ipfs/%{name}
%global tag     v0.6.0-rc7

Name:           go-ipfs
Version:        0.6.0~rc.7
Release:        1%{?dist}
Summary:        IPFS implementation in Go

License:        MIT and Apache-2.0
URL:            https://ipfs.io
Source0:        https://github.com/ipfs/%{name}/releases/download/%{tag}/%{name}-source.tar.gz
Source10:       ipfs.service
Source11:       ipfs.sysusers

%gometa

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
install -D %SOURCE11 %{buildroot}%{_sysusersdir}/ipfs.conf


%pre
%sysusers_create_package ipfs %SOURCE11

%post
%systemd_post ipfs.service

%preun
%systemd_preun ipfs.service

%postun
%systemd_postun ipfs.service


%files
%license LICENSE LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md
%{_bindir}/ipfs
%{_unitdir}/ipfs.service
%{_sysusersdir}/ipfs.conf
%dir %attr(775,ipfs,ipfs) %{_sharedstatedir}/ipfs


%if %{with devel}
%files devel -f devel.file-list
%license LICENSE LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md
%endif


%changelog
* Wed Jun 17 2020 ElXreno <elxreno@gmail.com> - 0.6.0~rc.7-1
- Updated to version 0.6.0-rc7

* Tue Jun 02 2020 ElXreno <elxreno@gmail.com> - 0.6.0~rc.1-1
- Update to version 0.6.0-rc.1

* Tue May 19 2020 gasinvein <gasinvein@gmail.com> - 0.5.1-0.2
- Add systemd units

* Mon May 18 2020 gasinvein <gasinvein@gmail.com> - 0.5.1-0.1
- Initial package
