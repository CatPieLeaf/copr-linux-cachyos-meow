%define _mok_dir /etc/kernel/certs/meow-kernel
%define _mok_key %{_mok_dir}/mok.key
%define _mok_der %{_mok_dir}/mok.der
%define _mok_pem %{_mok_dir}/mok.pem

# Fedora bits
%define __spec_install_post %{__os_install_post}
%define _build_id_links none
%define _default_patch_fuzz 2
%define _disable_source_fetch 0
%define debug_package %{nil}
%define make_build make %{?_lto_args} %{?_smp_mflags}
%undefine __brp_mangle_shebangs
%undefine _auto_set_build_flags
%undefine _include_frame_pointers

# Linux Kernel Versions
%define _basekver 7.0
%define _stablekver 0
%define _rpmver %{version}-%{release}
%define _kver %{_rpmver}.%{_arch}

%define _tarkver 7.0-rc5

%define _tag cachyos-%{_tarkver}-2
%define _meow_tag meow

# Patch version tracker - bump when CachyOS releases multiple
# patch revisions for the same kernel version
%define _patchver 3

# Build a minimal a kernel via modprobed.db
# file to reduce build times
%define _build_minimal 0

# Builds the kernel with clang and enables
# FullLTO
%define _build_lto 1

# Builds nvidia-open kernel modules with
# the kernel
%define _nv_pkg open-gpu-kernel-modules-%{_nv_ver}
# NVIDIA 595.45.04 - Latest bleeding-edge beta (2026-03-05)
# Highlights: VK_EXT_descriptor_heap, VK_EXT_present_timing, Wayland 1.20,
#             DRI3 1.2, modeset=1 by default, improved power management
# Previous stable: 580.126.18
%if 0%{?fedora} >= 43
    %define _build_nv 1
    %define _nv_ver 595.45.04
%elif 0%{?rhel}
    %define _build_nv 0
%else
    %define _build_nv 1
    %define _nv_ver 595.45.04
%endif

# Define the tickrate used by the kernel
# Valid values: 100, 250, 300, 500, 600, 750 and 1000
# An invalid value will not fail and continue to use
# 1000Hz tickrate
%define _hz_tick 1000

# Defines the x86_64 ISA level used
# to compile the kernel
# Valid values are 1-4
# An invalid value will continue and use
# x86_64_v3
%define _x86_64_lvl 3

# Define variables for directory paths
# to be used during packaging
%define _kernel_dir /lib/modules/%{_kver}
%define _devel_dir %{_usrsrc}/kernels/%{_kver}

%define _patch_src https://raw.githubusercontent.com/CachyOS/kernel-patches/master/%{_basekver}

%if %{_build_lto}
    # Define build environment variables to build the kernel with clang
    %define _lto_args CC=clang CXX=clang++ LD=ld.lld LLVM=1 LLVM_IAS=1

    # Alderlake native tuning flags
    %define _arch_cflags -march=alderlake -mtune=alderlake

    # -O3 optimization
    %define _opt_cflags -O3

    # Combined KCFLAGS for the build
    %define _kcflags %{_arch_cflags} %{_opt_cflags}
%endif

%define _module_args KERNEL_UNAME=%{_kver} IGNORE_PREEMPT_RT_PRESENCE=1 SYSSRC=%{_builddir}/linux-%{_tag} SYSOUT=%{_builddir}/linux-%{_tag}

Name:           kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag}
Summary:        Linux BORE %{?_lto_args:+ Full-LTO }Cachy Sauce Kernel - Alderlake/O3/BOLT/Rust - meow edition
Version:        %{_basekver}.%{_stablekver}
Release:        x64v%{_x86_64_lvl}_cachyos%{_patchver}%{?_lto_args:.lto}.%{_meow_tag}%{?dist}
License:        GPL-2.0-only
URL:            https://cachyos.org

Requires:       kernel-core-uname-r = %{_kver}
Requires:       kernel-modules-uname-r = %{_kver}
Requires:       kernel-modules-core-uname-r = %{_kver}
Provides:       kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag} > 6.12.9-cb1.0%{?_lto_args:.lto}.%{_meow_tag}%{?dist}
Provides:       installonlypkg(kernel)
Obsoletes:      kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag} <= 6.12.9-cb1.0.lto.%{_meow_tag}%{?dist}

BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  dwarves
BuildRequires:  elfutils-devel
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gettext-devel
BuildRequires:  kmod
BuildRequires:  make
BuildRequires:  openssl
BuildRequires:  openssl-devel
BuildRequires:  perl-Carp
BuildRequires:  perl-devel
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  python3-devel
BuildRequires:  python3-pyyaml
BuildRequires:  python-srpm-macros
BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  polly
BuildRequires:  pesign
BuildRequires:  nss-tools

%if %{_build_nv}
BuildRequires:  gcc-c++
%endif

# Indexes 0-9 are reserved for the kernel. 10-19 will be reserved for NVIDIA
Source0:        https://github.com/CachyOS/linux/archive/refs/tags/%{_tag}.tar.gz
Source1:        https://raw.githubusercontent.com/CachyOS/linux-cachyos/master/linux-cachyos/config

%if %{_build_minimal}
# The default modprobed.db provided is used for linux-cachyos CI.
# This should not be used for production and ideally should only be used for compile tests.
# Note that any modprobed.db file is accepted
Source2:        https://raw.githubusercontent.com/Frogging-Family/linux-tkg/master/linux-tkg-config/%{_basekver}/minimal-modprobed.db
%endif

%if %{_build_nv}
Source10:       https://github.com/NVIDIA/open-gpu-kernel-modules/archive/%{_nv_ver}/%{_nv_pkg}.tar.gz
%endif

Patch1:         %{_patch_src}/sched/0001-bore-cachy.patch
Patch2:         %{_patch_src}/0002-bbr3.patch
Patch3:         %{_patch_src}/misc/0001-acpi-call.patch
Patch4:         %{_patch_src}/misc/0001-cgroup-vram.patch
Patch5:         %{_patch_src}/misc/0001-clang-polly.patch

%if %{_build_lto}
Patch6:         %{_patch_src}/misc/dkms-clang.patch
%endif

%description
    The meta package for %{name}.

%prep
%setup -q %{?SOURCE10:-b 10} -n linux-%{_tag}
%patch -P 1 -p1
%patch -P 2 -p1
%patch -P 3 -p1
%patch -P 4 -p1
%patch -P 5 -p1
%if %{_build_lto}
%patch -P 6 -p1
%endif

    cp %{SOURCE1} .config

    # Default configs to always enable
    # Enable CACHY sauce and the scheduler
    # used in the default linux-cachyos kernel
    scripts/config -e CACHY -e SCHED_BORE

    # Use SElinux by default
    # https://github.com/sirlucjan/copr-linux-cachyos/pull/1
    scripts/config --set-str CONFIG_LSM lockdown,yama,integrity,selinux,bpf,landlock,apparmor

    # Do not change the system's hostname
    scripts/config -u DEFAULT_HOSTNAME

    case %{_hz_tick} in
        100|250|300|500|600|750|1000)
            scripts/config -e HZ_%{_hz_tick} --set-val HZ %{_hz_tick};;
        *)
            echo "Invalid tickrate value, using default 1000"
            scripts/config -e HZ_1000 --set-val HZ 1000;;
    esac

    %if %{_x86_64_lvl} < 5 && %{_x86_64_lvl} > 0
        scripts/config --set-val X86_64_VERSION %{_x86_64_lvl}
    %else
        echo "Invalid x86_64 ISA Level. Using x86_64_v3"
        scripts/config --set-val X86_64_VERSION 3
    %endif

    # Enable Secure boot support
    scripts/config -e CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT
    scripts/config -e CONFIG_IMA
    scripts/config -e CONFIG_IMA_APPRAISE_BOOTPARAM
    scripts/config -e CONFIG_IMA_APPRAISE
    scripts/config -e CONFIG_IMA_ARCH_POLICY
    scripts/config -d CONFIG_IMA_DEFAULT_HASH_SHA1
    scripts/config -e CONFIG_IMA_DEFAULT_HASH_SHA256
    scripts/config --set-str CONFIG_IMA_DEFAULT_HASH "sha256"
    scripts/config -e CONFIG_IMA_APPRAISE_MODSIG


    %if %{_build_lto}
        # Full LTO (not Thin) for maximum IPO
        scripts/config -d LTO_CLANG_THIN -e LTO_CLANG_FULL

        # Enable Polly loop optimizations
        # The clang-polly patch adds CONFIG_POLLY_CLANG option to Kconfig
        # We need to explicitly enable it here
        scripts/config -e POLLY_CLANG

        # Force Alderlake native tuning at kernel level
    %endif

    # Rust experimental features
    # Disable BTF to allow RUST + LTO to coexist
    scripts/config -d DEBUG_INFO_BTF
    scripts/config -d MODVERSIONS

    # Secure Boot: full kernel-level support
    # These configs embed a machine-owner key slot and enable module signature enforcement
    scripts/config -e MODULE_SIG
    scripts/config -e MODULE_SIG_ALL
    scripts/config -e MODULE_SIG_SHA512
    scripts/config --set-str MODULE_SIG_HASH sha512
    scripts/config -e MODULE_SIG_FORCE
    scripts/config -e SECURITY_LOCKDOWN_LSM
    scripts/config -e SECURITY_LOCKDOWN_LSM_EARLY
    scripts/config -e LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY
    scripts/config -e SYSTEM_TRUSTED_KEYRING
    scripts/config -e SYSTEM_EXTRA_CERTIFICATE
    scripts/config --set-val SYSTEM_EXTRA_CERTIFICATE_SIZE 4096
    scripts/config -e INTEGRITY_SIGNATURE
    scripts/config -e INTEGRITY_ASYMMETRIC_KEYS

    # PREEMPT_LAZY: modern lazy preemption model (better latency than PREEMPT,
    # better throughput than full PREEMPT_RT, default in linux-cachyos)
    scripts/config -e CONFIG_PREEMPT_BUILD
    scripts/config -e CONFIG_ARCH_HAS_PREEMPT_LAZY
    scripts/config -d CONFIG_PREEMPT
    scripts/config -d CONFIG_PREEMPT_VOLUNTARY
    scripts/config -d CONFIG_PREEMPT_RT
    scripts/config -e CONFIG_PREEMPT_LAZY

    # POC Selector: lets you switch scheduler at runtime
    scripts/config -e CONFIG_SCHED_POC_SELECTOR

    # Reflex frequency governor
    scripts/config -e CPU_FREQ_GOV_REFLEX

    # Tell the kernel Kconfig system we want -O3 (complements KCFLAGS=-O3)
    scripts/config -d CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE
    scripts/config -e CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE_O3

    # --- Intel Alder Lake (i7-12700H) ---
    scripts/config -e INTEL_PSTATE
    scripts/config -e SCHED_MC_PRIO        # Intel Thread Director / ITMT
    scripts/config -e INTEL_TCC_COOLING    # Intel thermal control

    # --- ASUS TUF Gaming ---
    scripts/config -e ASUS_WMI
    scripts/config -e ASUS_NB_WMI          # fans, hotkeys, thermal profiles
    scripts/config -e ACPI_WMI

    # --- Performance ---
    scripts/config -e LRU_GEN              # MGLRU
    scripts/config -e LRU_GEN_ENABLED
    scripts/config -e LRU_GEN_STATS

    %if %{_build_minimal}
        %make_build LSMOD=%{SOURCE2} localmodconfig
    %else
        %make_build olddefconfig
    %endif

    # Rust must be configured AFTER the first olddefconfig pass — if set before,
    # olddefconfig silently resets it because rpmbuild does not inherit the rustup PATH.
    export PATH="$HOME/.cargo/bin:$HOME/.rustup/toolchains/$(ls $HOME/.rustup/toolchains/ 2>/dev/null | grep -v tmp | head -1)/bin:$PATH"
    rustup component add rust-src 2>/dev/null || true
    echo "rustc: $(rustc --version 2>/dev/null || echo NOT FOUND)"
    echo "bindgen: $(bindgen --version 2>/dev/null || echo NOT FOUND)"
    echo "rust-src: $(rustup component list --installed 2>/dev/null | grep rust-src || echo NOT FOUND)"
    scripts/config -e RUST
    scripts/config -e RUST_OVERFLOW_CHECKS
    scripts/config -e RUST_PHYLIB_ABSTRACTIONS
    scripts/config -e SAMPLES_RUST
    %make_build olddefconfig

    # Enable BBRv3 with FQ qdisc - MUST be after olddefconfig to prevent reset
    # CRITICAL: BBR must be built-in (=y) not module (=m) to be set as default in Kconfig
    scripts/config --enable CONFIG_TCP_CONG_BBR
    scripts/config --enable CONFIG_TCP_CONG_CUBIC
    scripts/config --disable CONFIG_DEFAULT_CUBIC
    scripts/config --enable CONFIG_DEFAULT_BBR
    scripts/config --set-str CONFIG_DEFAULT_TCP_CONG bbr
    
    # Use FQ (Fair Queue) as default qdisc for BBR
    scripts/config --enable CONFIG_NET_SCH_FQ
    scripts/config --disable CONFIG_DEFAULT_FQ_CODEL
    scripts/config --enable CONFIG_DEFAULT_FQ
    scripts/config --set-str CONFIG_DEFAULT_NET_SCH fq

    # CPU arch: must be set AFTER all olddefconfig passes — it is a Kconfig choice
    # block and olddefconfig always resets it back to GENERIC_CPU (the default).
    %if %{_build_lto}
        scripts/config -d GENERIC_CPU -e X86_NATIVE_CPU -e MNATIVE_INTEL
    %endif

    diff -u %{SOURCE1} .config || :

%build
%if %{_build_lto}
    %make_build EXTRAVERSION=-%{release}.%{_arch} \
        KCFLAGS="%{_kcflags}" \
        KRUSTFLAGS="-Ctarget-cpu=alderlake -Copt-level=3" \
        all
%else
    %make_build EXTRAVERSION=-%{release}.%{_arch} all
%endif

    # Build bpftool vmlinux.h for devel package
    %make_build -C tools/bpf/bpftool vmlinux.h feature-clang-bpf-co-re=1 || true

    %if %{_build_nv}
        cd %{_builddir}/%{_nv_pkg}
        CFLAGS= CXXFLAGS= LDFLAGS= %make_build %{?_lto_args} %{_module_args} IGNORE_CC_MISMATCH=yes modules
    %endif

%install
    # 1. Install kernel modules
    echo "Installing kernel modules..."
    ZSTD_CLEVEL=19 %make_build INSTALL_MOD_PATH="%{buildroot}" INSTALL_MOD_STRIP=1 DEPMOD=/doesnt/exist modules_install

    # 2. Install and compress NVIDIA modules (prepare for signing)
    %if %{_build_nv}
        echo "Installing NVIDIA modules..."
        cd %{_builddir}/%{_nv_pkg}
        install -Dt %{buildroot}%{_kernel_dir}/nvidia -m644 kernel-open/*.ko
        find %{buildroot}%{_kernel_dir}/nvidia -name '*.ko' -exec zstd -19 --rm {} \;
        install -Dt %{buildroot}/%{_defaultlicensedir}/%{name}-nvidia-open -m644 COPYING
        cd %{_builddir}/linux-%{_tag}
    %endif

    # 3. Ensure Permanent MOK Key
    # Try /etc/kernel/certs first (persistent across rebuilds),
    # falls back to $HOME if /etc/kernel is not writable.
    MOK_CN="kernel-cachyos-lto-meow Secure Boot"
    if [ -w "/etc/kernel/certs" ] || ( [ ! -e "/etc/kernel/certs" ] && [ -w "/etc/kernel" ] ); then
        MOK_DIR="%{_mok_dir}"
    elif [ -w "/etc/kernel" ]; then
        MOK_DIR="%{_mok_dir}"
    else
        MOK_DIR="$HOME/.config/kernel-certs/meow-kernel"
    fi
    MOK_KEY="${MOK_DIR}/mok.key"
    MOK_DER="${MOK_DIR}/mok.der"
    MOK_PEM="${MOK_DIR}/mok.pem"

    if [ ! -f "${MOK_KEY}" ]; then
        mkdir -p "${MOK_DIR}"
        chmod 700 "${MOK_DIR}"
        openssl req -new -x509 -newkey rsa:4096 \
            -keyout "${MOK_KEY}" \
            -outform DER -out "${MOK_DER}" \
            -nodes -days 36500 \
            -subj "/CN=${MOK_CN}/" \
            -addext "extendedKeyUsage=codeSigning"
        chmod 600 "${MOK_KEY}"
        openssl x509 -inform DER -in "${MOK_DER}" -out "${MOK_PEM}"
        echo "MOK key generated at ${MOK_DIR}"
    else
        echo "Reusing existing MOK key from ${MOK_DIR}"
    fi

    # 4. Install and sign vmlinuz (Kernel Image)
    echo "Installing and signing kernel image..."
    SB_VMLINUZ="%{buildroot}%{_kernel_dir}/vmlinuz"
    install -Dm644 "$(%make_build -s image_name)" "$SB_VMLINUZ"

    TMP_NSS=$(mktemp -d)
    trap "rm -rf $TMP_NSS" EXIT
    certutil -d "$TMP_NSS" -N --empty-password
    openssl pkcs12 -export -out "$TMP_NSS/sb.p12" \
        -inkey "${MOK_KEY}" -in "${MOK_PEM}" \
        -name "${MOK_CN}" -passout pass:
    pk12util -i "$TMP_NSS/sb.p12" -d "$TMP_NSS" -W ""
    pesign -n "$TMP_NSS" -c "${MOK_CN}" --sign \
           -i "$SB_VMLINUZ" -o "$SB_VMLINUZ.signed"
    mv "$SB_VMLINUZ.signed" "$SB_VMLINUZ"
    trap - EXIT
    rm -rf "$TMP_NSS"

    # 5. Sign ALL modules (.ko.zst) - Kernel + NVIDIA
    echo "Signing all modules for Secure Boot..."
    SIGN_SCRIPT="%{_builddir}/linux-%{_tag}/scripts/sign-file"

    while IFS= read -r KO; do
        UNZST="${KO%.zst}"
        if ! zstd -d --rm "${KO}" -o "${UNZST}"; then
            echo "ERROR: failed to decompress ${KO}" >&2
            exit 1
        fi
        if ! "${SIGN_SCRIPT}" sha512 "${MOK_KEY}" "${MOK_PEM}" "${UNZST}"; then
            echo "ERROR: failed to sign ${UNZST}" >&2
            exit 1
        fi
        if ! zstd -19 --rm "${UNZST}" -o "${KO}"; then
            echo "ERROR: failed to recompress ${UNZST}" >&2
            exit 1
        fi
    done < <(find "%{buildroot}%{_kernel_dir}" -name "*.ko.zst")

    # 6. Development files setup (Fedora parity)
    zstdmt -19 < Module.symvers > %{buildroot}%{_kernel_dir}/symvers.zst
    # Install der to kernel-specific path (for reference) AND to fixed permanent path
    install -Dm644 "${MOK_DER}" "%{buildroot}%{_kernel_dir}/secureboot-meow.der"
    install -Dm644 "${MOK_DER}" "%{buildroot}/etc/kernel/certs/meow-kernel/mok.der"

    install -Dt %{buildroot}%{_devel_dir} -m644 .config Makefile Module.symvers System.map
    [ -f tools/bpf/bpftool/vmlinux.h ] && install -m644 tools/bpf/bpftool/vmlinux.h %{buildroot}%{_devel_dir}/ || true
    cp .config %{buildroot}%{_kernel_dir}/config
    cp System.map %{buildroot}%{_kernel_dir}/System.map
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}%{_devel_dir}
    rm -rf %{buildroot}%{_devel_dir}/scripts
    rm -rf %{buildroot}%{_devel_dir}/include
    cp -a scripts %{buildroot}%{_devel_dir}
    rm -rf %{buildroot}%{_devel_dir}/scripts/tracing
    rm -f %{buildroot}%{_devel_dir}/scripts/spdxcheck.py

    # The cp commands below are needed for parity with Fedora's packaging
    # Install files that are needed for `make scripts` to succeed
    cp -a --parents security/selinux/include/classmap.h %{buildroot}%{_devel_dir}
    cp -a --parents security/selinux/include/initial_sid_to_string.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/be_byteshift.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/le_byteshift.h %{buildroot}%{_devel_dir}

    # Install files that are needed for `make prepare` to succeed -- Generic
    cp -a --parents tools/include/linux/compiler* %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux/types.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/build/Build.include %{buildroot}%{_devel_dir}
    cp --parents tools/build/fixdep.c %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/sync-check.sh %{buildroot}%{_devel_dir}
    cp -a --parents tools/bpf/resolve_btfids %{buildroot}%{_devel_dir}

    cp --parents security/selinux/include/policycap_names.h %{buildroot}%{_devel_dir}
    cp --parents security/selinux/include/policycap.h %{buildroot}%{_devel_dir}

    cp -a --parents tools/include/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/asm-generic %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm-generic %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/linux %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/vdso %{buildroot}%{_devel_dir}
    cp --parents tools/scripts/utilities.mak %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/subcmd %{buildroot}%{_devel_dir}
    cp --parents tools/lib/*.c %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/*.[ch] %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/Build %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/include/objtool/*.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/bpf %{buildroot}%{_devel_dir}
    cp --parents tools/lib/bpf/Build %{buildroot}%{_devel_dir}

    # Misc headers
    cp -a --parents arch/x86/include %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include %{buildroot}%{_devel_dir}
    cp -a include %{buildroot}%{_devel_dir}/include
    cp -a sound/soc/sof/sof-audio.h %{buildroot}%{_devel_dir}/sound/soc/sof
    cp -a tools/objtool/objtool %{buildroot}%{_devel_dir}/tools/objtool/
    cp -a tools/objtool/fixdep %{buildroot}%{_devel_dir}/tools/objtool/

    # Install files that are needed for `make prepare` to succeed -- for x86_64
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_32.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_64.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_common.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.h %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/purgatory.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/stack.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/setup-x86_64.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/entry64.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.h %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/ctype.h %{buildroot}%{_devel_dir}

    cp -a --parents scripts/syscalltbl.sh %{buildroot}%{_devel_dir}
    cp -a --parents scripts/syscallhdr.sh %{buildroot}%{_devel_dir}

    cp -a --parents tools/arch/x86/include/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include/uapi/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/objtool/arch/x86/lib %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/lib/ %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk %{buildroot}%{_devel_dir}
    cp -a --parents tools/objtool/arch/x86/ %{buildroot}%{_devel_dir}

    # Final cleanups ala Fedora
    echo "Cleaning up development files..."
    find %{buildroot}%{_devel_dir}/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    find %{buildroot}%{_devel_dir}/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    touch -r %{buildroot}%{_devel_dir}/Makefile \
        %{buildroot}%{_devel_dir}/include/generated/uapi/linux/version.h \
        %{buildroot}%{_devel_dir}/include/config/auto.conf

    # These links will be owned by the modules package, creating a broken
    # link unless the -devel package is installed. why??
    rm -rf %{buildroot}%{_kernel_dir}/build
    ln -s %{_devel_dir} %{buildroot}%{_kernel_dir}/build
    ln -s %{_kernel_dir}/build %{buildroot}%{_kernel_dir}/source

    # Create stub initramfs to inflate disk space requirements.
    # This should hopefully prevent some initramfs failures due to
    # insufficient space in /boot (#bz #530778)
    # 90 seems to be a safe value nowadays. It is slightly inflated than the
    # measured average to also account for installed vmlinuz in /boot
    echo "Creating stub initramfs..."
    install -dm755 %{buildroot}/boot
    dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{_kver}.img bs=1M count=90

%package core
Summary:        Linux BORE Cachy Sauce Kernel by CachyOS with other patches and improvements
AutoReq:        no
Conflicts:      xfsprogs < 4.3.0-1
Conflicts:      xorg-x11-drv-vmmouse < 13.0.99
Provides:       kernel = %{_rpmver}
Provides:       kernel-core-uname-r = %{_kver}
Provides:       kernel-uname-r = %{_kver}
Provides:       installonlypkg(kernel)
Requires:       kernel-modules-uname-r = %{_kver}
Requires:       nvidia-gpu-firmware
Requires(pre):  /usr/bin/kernel-install
Requires(pre):  coreutils
Requires(pre):  dracut >= 027
Requires(pre):  systemd >= 203-2
Requires(pre):  ((linux-firmware >= 20150904-56.git6ebf5d57) if linux-firmware)
Requires(preun):systemd >= 200
Recommends:     linux-firmware

%description core
    The kernel package contains the Linux kernel (vmlinuz), the core of any
    Linux operating system.  The kernel handles the basic functions
    of the operating system: memory allocation, process allocation, device
    input and output, etc.

%post core
    mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
    touch %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver}

%posttrans core
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver}
    if [ ! -e /run/ostree-booted ]; then
        /bin/kernel-install add %{_kver} %{_kernel_dir}/vmlinuz || exit $?
        if [[ ! -e "/boot/symvers-%{_kver}.zst" ]]; then
            cp "%{_kernel_dir}/symvers.zst" "/boot/symvers-%{_kver}.zst"
            if command -v restorecon &>/dev/null; then
                restorecon "/boot/symvers-%{_kver}.zst"
            fi
        fi
    fi
    # Secure Boot: remind user to enroll the MOK key if not yet enrolled
    if [ -f "%{_kernel_dir}/secureboot-meow.der" ]; then
        if command -v mokutil &>/dev/null; then
            SB_STATE=$(mokutil --sb-state 2>/dev/null || true)
            echo ""
            echo "======================================================================"
            echo " kernel-cachyos-lto-meow: Secure Boot key enrollment"
            echo "======================================================================"
            echo " A self-signed MOK key was embedded during build."
            echo " Current Secure Boot state: ${SB_STATE:-unknown}"
            echo " To enroll the key, run:"
            echo "   mokutil --import /etc/kernel/certs/meow-kernel/mok.der"
            echo " (This key is permanent — you only need to enroll it once)"
            echo " Then reboot and confirm enrollment in the MOK Manager (shim)."
            echo "======================================================================"
        fi
    fi

%preun core
    /bin/kernel-install remove %{_kver} || exit $?
    if [ -x /usr/sbin/weak-modules ]; then
        /usr/sbin/weak-modules --remove-kernel %{_kver} || exit $?
    fi

%files core
    %license COPYING
    %ghost %attr(0600, root, root) /boot/initramfs-%{_kver}.img
    %ghost %attr(0644, root, root) /boot/symvers-%{_kver}.zst
    %{_kernel_dir}/vmlinuz
    %{_kernel_dir}/modules.builtin
    %{_kernel_dir}/modules.builtin.modinfo
    %{_kernel_dir}/symvers.zst
    %{_kernel_dir}/config
    %{_kernel_dir}/System.map
    %{_kernel_dir}/secureboot-meow.der
    /etc/kernel/certs/meow-kernel/mok.der

%package modules
Summary:        Kernel modules package for %{name}
Provides:       kernel-modules = %{_rpmver}
Provides:       kernel-modules-core = %{_rpmver}
Provides:       kernel-modules-extra = %{_rpmver}
Provides:       kernel-modules-uname-r = %{_kver}
Provides:       kernel-modules-core-uname-r = %{_kver}
Provides:       kernel-modules-extra-uname-r = %{_kver}
Provides:       v4l2loopback-kmod = 0.14.0
Provides:       installonlypkg(kernel-module)
Requires:       kernel-uname-r = %{_kver}
%if %{_build_lto}
Requires:       clang llvm llvm-devel lld
%endif

%description modules
    This package provides kernel modules for the %{name}-core kernel package.

%post modules
    if [ ! -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver} ]; then
        mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
        touch %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}
    fi

%posttrans modules
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}
    /sbin/depmod -a %{_kver}
    if [ ! -e /run/ostree-booted ]; then
        if [ -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver} ]; then
            echo "Running: dracut -f --kver %{_kver}"
            dracut -f --kver "%{_kver}" || exit $?
        fi
    fi

%files modules
    %dir %{_kernel_dir}
    %{_kernel_dir}/modules.order
    %{_kernel_dir}/build
    %{_kernel_dir}/source
    %{_kernel_dir}/kernel

%package devel
Summary:        Development package for building kernel modules to match %{name}
Provides:       kernel-devel = %{_rpmver}
Provides:       kernel-devel-uname-r = %{_kver}
Provides:       installonlypkg(kernel)
AutoReqProv:    no
Requires(pre):  findutils
Requires:       findutils
Requires:       perl-interpreter
Requires:       openssl-devel
Requires:       elfutils-libelf-devel
Requires:       bison
Requires:       flex
Requires:       make

%if %{_build_lto}
Requires:       clang
Requires:       lld
Requires:       llvm
%else
Requires:       gcc
%endif

%description devel
    This package provides kernel headers and makefiles sufficient to build modules against %{name}.

%post devel
    if [ -f /etc/sysconfig/kernel ]; then
        . /etc/sysconfig/kernel || exit $?
    fi
    if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ]; then
        (cd /usr/src/kernels/%{_kver} &&
        /usr/bin/find . -type f | while read f; do
            hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f > /dev/null
        done;
        )
    fi

%files devel
    %{_devel_dir}

%package devel-matched
Summary:        Meta package to install matching core and devel packages for %{name}
Provides:       kernel-devel-matched = %{_rpmver}
Requires:       %{name}-core = %{_rpmver}
Requires:       %{name}-devel = %{_rpmver}

%description devel-matched
    This meta package is used to install matching core and devel packages for %{name}.

%files devel-matched

%if %{_build_nv}
%package nvidia-open
Summary:        nvidia-open %{_nv_ver} kernel modules for %{name}
Provides:       nvidia-kmod >= %{_nv_ver}
Provides:       installonlypkg(kernel-module)
Requires:       kernel-uname-r = %{_kver}
Conflicts:      akmod-nvidia

%description nvidia-open
    This package provides nvidia-open %{_nv_ver} kernel modules for %{name}.

%post nvidia-open
    /sbin/depmod -a %{_kver}
    mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
    touch %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}

%posttrans nvidia-open
    /sbin/depmod -a %{_kver}
    if [ -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver} ]; then
        rm -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}
        echo "Running: dracut -f --kver %{_kver}"
        dracut -f --kver "%{_kver}" || exit $?
    fi

%files nvidia-open
    %license %{_defaultlicensedir}/%{name}-nvidia-open/COPYING
    %{_kernel_dir}/nvidia
%endif

%files

%changelog
* Mon Mar 23 2026 meow build <meow@localhost> - 7.0.0-1
- Bump to CachyOS Linux 7.0-rc5-1 (based on Linux 7.0-rc5)
- Applied patches:
  * BORE-CACHY scheduler patch
  * BBRv3 TCP congestion control
  * ACPI call support
  * cgroup VRAM support
  * Clang Polly optimizations (CONFIG_POLLY_CLANG=y)
  * DKMS Clang support (LTO builds only)
- Compiler optimizations:
  * Full LTO enabled (CONFIG_LTO_CLANG_FULL=y)
  * O3 optimization level (CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE_O3=y)
  * Polly loop optimizations (CONFIG_POLLY_CLANG=y enables -mllvm -polly flags)
  * Alderlake native tuning (-march=alderlake -mtune=alderlake)
- Removed patches incompatible with 7.0-rc5:
  * vmscape mitigations (does not apply to 7.0-rc5)
  * NVIDIA driver patches (require separate application to NVIDIA module sources)
  * handheld, rt-i915, poc-selector, reflex-governor
- Note: NVIDIA modules will be built without additional patches

* Sat Mar 14 2026 meow build <meow@localhost> - 6.19.8-1
- Enabled BBRv3 as default TCP congestion control algorithm

* Thu Mar 12 2026 meow build <meow@localhost> - 6.19.7-1
- Bump to CachyOS Linux 6.19.7-1 (based on Linux 6.19.7)
- ADIOS scheduler bumped to v3.1.9
- BORE scheduler updated (BORE-CACHY patch)
- Cachy: ADIOS v3.1.7 -> v3.1.9 progression
- New: AMD ISP4 capture driver (amd-isp4)
- New: HDMI VRR over PCON + ALLM support (amdgpu)
- New: VESA DSC BPP target parsing from EDID
- New: vmscape mitigations (BHB clearing, static_call)
- New: T2 Mac support patches (apple-bce, magicmouse SPI, applesmc MMIO)
- Fixes: sched_ext, amdgpu unload hang, i915 RC6, iommu 0x0 mapping,
         ACPI s2idle, netfilter nf_tables, USB quirks, ALSA Acer quirk
- Reset _patchver to 1

* Sat Mar 07 2026 meow build <meow@localhost> - 6.19.6-1
- Initial meow build
