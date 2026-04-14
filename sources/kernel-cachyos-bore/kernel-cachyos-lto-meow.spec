# ==============================================================================
# MOK certificate paths
# ==============================================================================
%define _mok_dir /etc/kernel/certs/meow-kernel
%define _mok_der %{_mok_dir}/mok.der
%define _mok_key %{_mok_dir}/mok.key
%define _mok_pem %{_mok_dir}/mok.pem

# ==============================================================================
# Platform guard — Fedora only
# ==============================================================================
%if 0%{?rhel}
%{error: Building on RHEL/CentOS/AlmaLinux is not supported. This spec targets Fedora only.}
%endif

# ==============================================================================
# Build system overrides
# ==============================================================================
%define __spec_install_post   %{__os_install_post}
%define _build_id_links       none
%define _default_patch_fuzz   2
%define _disable_source_fetch 0
%define debug_package         %{nil}
%define make_build            make %{?_lto_args} %{?_smp_mflags}
%undefine __brp_mangle_shebangs
%undefine _auto_set_build_flags
%undefine _include_frame_pointers

# ==============================================================================
# Kernel version
# ==============================================================================
%define _basekver   7.0
%define _stablekver .0
# -rc0 or .0
%define _tarkver    %{_basekver}%{_stablekver}
%define _tag        cachyos-%{_tarkver}-2
%define _meow_tag   meow

# Bump when CachyOS releases multiple patch revisions for the same kernel version
%define _patchver 9

# Derived version strings
%define _rpmver %{version}-%{release}
%define _kver   %{_rpmver}.%{_arch}

# ==============================================================================
# Feature flags
# ==============================================================================

# Build a minimal kernel via modprobed.db to reduce build times.
# The default modprobed.db is intended for CI only, not production.
%define _build_minimal 0

# Build with Clang and enable Full LTO
%define _build_lto 1

# Enable Alder Lake-native tuning:
#   - -march/-mtune=alderlake in KCFLAGS
#   - -Ctarget-cpu=alderlake in KRUSTFLAGS
#   - Native Intel CPU Kconfig (MNATIVE_INTEL / X86_NATIVE_CPU)
#   - Intel hardware drivers (INTEL_PSTATE, INTEL_TCC_COOLING, SCHED_MC_PRIO)
%define _build_alderlake 1

# Tickrate: valid values are 100, 250, 300, 500, 600, 750, 1000.
# An invalid value will fall back to 1000 Hz.
%define _hz_tick 1000

# x86_64 ISA level: valid values are 1-4.
# An invalid value will fall back to x86_64_v3.
%define _x86_64_lvl 3

# ==============================================================================
# NVIDIA open kernel modules
# ==============================================================================
%define _build_nv 1
%define _nv_ver   595.58.03
%define _nv_pkg   open-gpu-kernel-modules-%{_nv_ver}

# ==============================================================================
# Directory paths
# ==============================================================================
%define _devel_dir  %{_usrsrc}/kernels/%{_kver}
%define _kernel_dir /lib/modules/%{_kver}
%define _patch_src  https://raw.githubusercontent.com/CachyOS/kernel-patches/master/%{_basekver}

# ==============================================================================
# LTO build environment (Clang / Full LTO / O3)
# ==============================================================================
%if %{_build_lto}
%define _lto_args   CC=clang CXX=clang++ LD=ld.lld LLVM=1 LLVM_IAS=1
%define _opt_cflags -O3

%if %{_build_alderlake}
%define _arch_cflags  -march=alderlake -mtune=alderlake
%define _kcflags      %{_arch_cflags} %{_opt_cflags}
%define _krustflags   -Ctarget-cpu=alderlake -Copt-level=3
%else
%define _kcflags      %{_opt_cflags}
%define _krustflags   -Copt-level=3
%endif
%endif

# ==============================================================================
# External module build arguments
# ==============================================================================
%define _module_args KERNEL_UNAME=%{_kver} IGNORE_PREEMPT_RT_PRESENCE=1 SYSSRC=%{_builddir}/linux-%{_tag} SYSOUT=%{_builddir}/linux-%{_tag}

# ==============================================================================
# Package metadata
# ==============================================================================
Name:    kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag}
Summary: Linux BORE %{?_lto_args:+ Full-LTO }Cachy Sauce Kernel - Alderlake/O3/BOLT/Rust - meow edition
Version: %{_basekver}%{_stablekver}
Release: x64v%{_x86_64_lvl}_cachyos%{_patchver}%{?_lto_args:.lto}.%{_meow_tag}%{?dist}
License: GPL-2.0-only
URL:     https://cachyos.org

Requires: kernel-core-uname-r        = %{_kver}
Requires: kernel-modules-core-uname-r = %{_kver}
Requires: kernel-modules-uname-r     = %{_kver}

Provides: installonlypkg(kernel)
Provides: kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag} > 6.12.9-cb1.0%{?_lto_args:.lto}.%{_meow_tag}%{?dist}

Obsoletes: kernel-cachyos%{?_lto_args:-lto}-%{_meow_tag} <= 6.12.9-cb1.0.lto.%{_meow_tag}%{?dist}

# ==============================================================================
# Build dependencies
# ==============================================================================
BuildRequires: bc
BuildRequires: bison
BuildRequires: dwarves
BuildRequires: elfutils-devel
BuildRequires: flex
BuildRequires: gcc
BuildRequires: gettext-devel
BuildRequires: kmod
BuildRequires: make
BuildRequires: openssl
BuildRequires: openssl-devel
BuildRequires: perl-Carp
BuildRequires: perl-devel
BuildRequires: perl-generators
BuildRequires: perl-interpreter
BuildRequires: python-srpm-macros
BuildRequires: python3-devel
BuildRequires: python3-pyyaml
# BuildRequires: rust
# Rust is provided via rustup, not the system package

%if %{_build_lto}
BuildRequires: clang
BuildRequires: lld
BuildRequires: llvm
BuildRequires: polly
%endif

%if %{_build_nv}
BuildRequires: gcc-c++
BuildRequires: nss-tools
BuildRequires: pesign
%endif

# ==============================================================================
# Sources
# Indexes 0-9 are reserved for the kernel; 10-19 for NVIDIA.
# ==============================================================================
Source0: https://github.com/CachyOS/linux/archive/refs/tags/%{_tag}.tar.gz
Source1: https://raw.githubusercontent.com/CachyOS/linux-cachyos/master/linux-cachyos-bore/config

%if %{_build_minimal}
Source2: https://raw.githubusercontent.com/Frogging-Family/linux-tkg/master/linux-tkg-config/%{_basekver}/minimal-modprobed.db
%endif

%if %{_build_nv}
Source10: https://github.com/NVIDIA/open-gpu-kernel-modules/archive/%{_nv_ver}/%{_nv_pkg}.tar.gz
%endif

# ==============================================================================
# Patches
# ==============================================================================

%if %{_build_lto}
Patch1: %{_patch_src}/misc/0001-clang-polly.patch
Patch2: %{_patch_src}/misc/dkms-clang.patch
%endif

Patch3: %{_patch_src}/sched-dev/0001-bore-cachy.patch
Patch4: %{_patch_src}/0002-bbr3.patch
Patch5: %{_patch_src}/misc/0001-acpi-call.patch

# ==============================================================================
%description
    The meta package for %{name}.

# ==============================================================================
%prep
# ==============================================================================
%setup -q %{?SOURCE10:-b 10} -n linux-%{_tag}
%if %{_build_lto}
%patch -P 1 -p1
%patch -P 2 -p1
%endif
%patch -P 3 -p1
%patch -P 4 -p1
%patch -P 5 -p1

    cp %{SOURCE1} .config

    # --- Base identity ---
    # Enable CachyOS sauce and the BORE scheduler
    scripts/config -e CACHY -e SCHED_BORE

    # SELinux as default LSM stack
    # https://github.com/sirlucjan/copr-linux-cachyos/pull/1
    scripts/config --set-str CONFIG_LSM lockdown,yama,integrity,selinux,bpf,landlock,apparmor

    # Do not override the system hostname
    scripts/config -u DEFAULT_HOSTNAME

    # --- Tickrate ---
    case %{_hz_tick} in
        100|250|300|500|600|750|1000)
            scripts/config -e HZ_%{_hz_tick} --set-val HZ %{_hz_tick};;
        *)
            echo "Invalid tickrate value, using default 1000"
            scripts/config -e HZ_1000 --set-val HZ 1000;;
    esac

    # --- x86_64 ISA level ---
    %if %{_x86_64_lvl} < 5 && %{_x86_64_lvl} > 0
        scripts/config --set-val X86_64_VERSION %{_x86_64_lvl}
    %else
        echo "Invalid x86_64 ISA Level. Using x86_64_v3"
        scripts/config --set-val X86_64_VERSION 3
    %endif

    # --- Secure Boot: IMA, module signing, and kernel lockdown ---
    # IMA (Integrity Measurement Architecture)
    scripts/config -e  CONFIG_IMA
    scripts/config -e  CONFIG_IMA_APPRAISE
    scripts/config -e  CONFIG_IMA_APPRAISE_BOOTPARAM
    scripts/config -e  CONFIG_IMA_APPRAISE_MODSIG
    scripts/config -e  CONFIG_IMA_ARCH_POLICY
    scripts/config -e  CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT
    scripts/config -d  CONFIG_IMA_DEFAULT_HASH_SHA1
    scripts/config -e  CONFIG_IMA_DEFAULT_HASH_SHA256
    scripts/config --set-str CONFIG_IMA_DEFAULT_HASH "sha256"

    # Module signing (SHA-512 enforced)
    scripts/config -e  MODULE_SIG
    scripts/config -e  MODULE_SIG_ALL
    scripts/config -e  MODULE_SIG_FORCE
    scripts/config -e  MODULE_SIG_SHA512
    scripts/config --set-str MODULE_SIG_HASH sha512

    # Kernel lockdown and integrity
    scripts/config -e  CONFIG_KEXEC_SIG
    scripts/config -e  INTEGRITY_ASYMMETRIC_KEYS
    scripts/config -e  INTEGRITY_SIGNATURE
    scripts/config -e  LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY
    scripts/config -e  SECURITY_LOCKDOWN_LSM
    scripts/config -e  SECURITY_LOCKDOWN_LSM_EARLY
    scripts/config -e  SYSTEM_EXTRA_CERTIFICATE
    scripts/config --set-val SYSTEM_EXTRA_CERTIFICATE_SIZE 4096
    scripts/config -e  SYSTEM_TRUSTED_KEYRING

    # --- LTO-specific configs ---
    %if %{_build_lto}
        # Full LTO (not Thin) for maximum IPO
        scripts/config -d CONFIG_LTO_NONE
        scripts/config -d CONFIG_LTO_CLANG_THIN
        scripts/config -d LTO_CLANG_THIN
        scripts/config -e CONFIG_LTO_CLANG_FULL
        scripts/config -e LTO_CLANG_FULL

        # Polly loop optimizations (enabled by the clang-polly patch)
        scripts/config -e POLLY_CLANG
    %endif

    # --- Rust compatibility ---
    # Disable BTF to allow Rust + LTO to coexist
    scripts/config -d DEBUG_INFO_BTF
    scripts/config -d MODVERSIONS

    # --- Preemption model ---
    # PREEMPT_LAZY: better latency than PREEMPT, better throughput than PREEMPT_RT
    scripts/config -e CONFIG_ARCH_HAS_PREEMPT_LAZY
    scripts/config -e CONFIG_PREEMPT_BUILD
    scripts/config -e CONFIG_PREEMPT_LAZY
    scripts/config -d CONFIG_PREEMPT
    scripts/config -d CONFIG_PREEMPT_RT
    scripts/config -d CONFIG_PREEMPT_VOLUNTARY

    # --- Scheduler ---
    # POC Selector: runtime scheduler switching
    scripts/config -e CONFIG_SCHED_POC_SELECTOR

    # --- CPU frequency ---
    scripts/config -e CPU_FREQ_GOV_REFLEX

    # --- Optimization level ---
    # Tell Kconfig we want -O3 (complements KCFLAGS=-O3)
    scripts/config -d CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE
    scripts/config -e CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE_O3

    # --- Hardware: Intel Alder Lake ---
    %if %{_build_alderlake}
    scripts/config -e INTEL_PSTATE
    scripts/config -e INTEL_TCC_COOLING
    scripts/config -e SCHED_MC_PRIO
    %endif

    # --- Hardware: ASUS TUF Gaming ---
    scripts/config -e ACPI_WMI
    scripts/config -e ASUS_NB_WMI
    scripts/config -e ASUS_WMI

    # --- Memory management: MGLRU ---
    scripts/config -e LRU_GEN
    scripts/config -e LRU_GEN_ENABLED
    scripts/config -e LRU_GEN_STATS

    # --- First config pass ---
    %if %{_build_minimal}
        %make_build LSMOD=%{SOURCE2} localmodconfig
    %else
        %make_build olddefconfig
    %endif

    # Rust must be configured AFTER the first olddefconfig pass — if set before,
    # olddefconfig silently resets it because rpmbuild does not inherit the rustup PATH.
    export PATH="$HOME/.cargo/bin:$HOME/.rustup/toolchains/$(ls $HOME/.rustup/toolchains/ 2>/dev/null | grep -v tmp | head -1)/bin:$PATH"
    rustup component add rust-src 2>/dev/null || true
    echo "rustc:    $(rustc   --version 2>/dev/null || echo NOT FOUND)"
    echo "bindgen:  $(bindgen --version 2>/dev/null || echo NOT FOUND)"
    echo "rust-src: $(rustup component list --installed 2>/dev/null | grep rust-src || echo NOT FOUND)"
    scripts/config -e RUST
    scripts/config -e RUST_OVERFLOW_CHECKS
    scripts/config -e RUST_PHYLIB_ABSTRACTIONS
    scripts/config -e SAMPLES_RUST
    %make_build olddefconfig

    # --- Networking: BBR v3 + FQ ---
    # BBR must be built-in (=y), not a module (=m), to be set as default in Kconfig.
    # These must come after olddefconfig to prevent being reset.
    scripts/config --enable  CONFIG_TCP_CONG_BBR
    scripts/config --enable  CONFIG_TCP_CONG_CUBIC
    scripts/config --disable CONFIG_DEFAULT_CUBIC
    scripts/config --enable  CONFIG_DEFAULT_BBR
    scripts/config --set-str CONFIG_DEFAULT_TCP_CONG bbr
    scripts/config --enable  CONFIG_NET_SCH_CAKE
    scripts/config --enable  CONFIG_NET_SCH_DEFAULT
    scripts/config --enable  CONFIG_NET_SCH_FQ
    scripts/config --enable  CONFIG_NET_SCH_FQ_CODEL

    # --- CPU arch: must be set AFTER all olddefconfig passes ---
    # Kconfig always resets it back to GENERIC_CPU (the default).
    %if %{_build_alderlake}
        scripts/config -d GENERIC_CPU -e MNATIVE_INTEL -e X86_NATIVE_CPU
    %endif

    diff -u %{SOURCE1} .config || :

# ==============================================================================
%build
# ==============================================================================
%if %{_build_lto}
    %make_build EXTRAVERSION=-%{release}.%{_arch} KCFLAGS="%{_kcflags}" KRUSTFLAGS="%{_krustflags}" all
%else
    %make_build EXTRAVERSION=-%{release}.%{_arch} all
%endif

    # Build bpftool vmlinux.h for the devel package
    %make_build -C tools/bpf/bpftool vmlinux.h feature-clang-bpf-co-re=1 || true

    %if %{_build_nv}
        cd %{_builddir}/%{_nv_pkg}
        CFLAGS= CXXFLAGS= LDFLAGS= %make_build %{?_lto_args} %{_module_args} IGNORE_CC_MISMATCH=yes modules
    %endif

# ==============================================================================
%install
# ==============================================================================

    # 1. Kernel modules
    echo "Installing kernel modules..."
    ZSTD_CLEVEL=19 %make_build INSTALL_MOD_PATH="%{buildroot}" INSTALL_MOD_STRIP=1 DEPMOD=/doesnt/exist modules_install

    # 2. NVIDIA modules (install and compress before signing)
    %if %{_build_nv}
        echo "Installing NVIDIA modules..."
        cd %{_builddir}/%{_nv_pkg}
        install -Dt %{buildroot}%{_kernel_dir}/nvidia -m644 kernel-open/*.ko
        find %{buildroot}%{_kernel_dir}/nvidia -name '*.ko' -exec zstd -19 --rm {} \;
        install -Dt %{buildroot}/%{_defaultlicensedir}/%{name}-nvidia-open -m644 COPYING
        cd %{_builddir}/linux-%{_tag}
    %endif

    # 3. MOK key — persistent across rebuilds
    # Tries /etc/kernel/certs first; falls back to $HOME if not writable.
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
        openssl req -new -x509 -newkey rsa:4096 -keyout "${MOK_KEY}" -outform DER -out "${MOK_DER}" -nodes -days 36500 -subj "/CN=${MOK_CN}/" -addext "extendedKeyUsage=codeSigning"
        chmod 600 "${MOK_KEY}"
        openssl x509 -inform DER -in "${MOK_DER}" -out "${MOK_PEM}"
        echo "MOK key generated at ${MOK_DIR}"
    else
        echo "Reusing existing MOK key from ${MOK_DIR}"
    fi

    # 4. Install and sign vmlinuz
    echo "Installing and signing kernel image..."
    SB_VMLINUZ="%{buildroot}%{_kernel_dir}/vmlinuz"
    install -Dm644 "$(%make_build -s image_name)" "$SB_VMLINUZ"

    TMP_NSS=$(mktemp -d)
    trap "rm -rf $TMP_NSS" EXIT
    certutil -d "$TMP_NSS" -N --empty-password
    openssl pkcs12 -export -out "$TMP_NSS/sb.p12" -inkey "${MOK_KEY}" -in "${MOK_PEM}" -name "${MOK_CN}" -passout pass:
    pk12util -i "$TMP_NSS/sb.p12" -d "$TMP_NSS" -W ""
    pesign -n "$TMP_NSS" -c "${MOK_CN}" --sign -i "$SB_VMLINUZ" -o "$SB_VMLINUZ.signed"
    mv "$SB_VMLINUZ.signed" "$SB_VMLINUZ"
    trap - EXIT
    rm -rf "$TMP_NSS"

    # 5. Sign all modules (.ko.zst) — kernel + NVIDIA
    echo "Signing all modules for Secure Boot..."
    SIGN_SCRIPT="%{_builddir}/linux-%{_tag}/scripts/sign-file"

    while IFS= read -r KO; do
        UNZST="${KO%.zst}"
        if ! zstd -d --rm "${KO}" -o "${UNZST}"; then
            echo "ERROR: failed to decompress ${KO}" >&2; exit 1
        fi
        if ! "${SIGN_SCRIPT}" sha512 "${MOK_KEY}" "${MOK_PEM}" "${UNZST}"; then
            echo "ERROR: failed to sign ${UNZST}" >&2; exit 1
        fi
        if ! zstd -19 --rm "${UNZST}" -o "${KO}"; then
            echo "ERROR: failed to recompress ${UNZST}" >&2; exit 1
        fi
    done < <(find "%{buildroot}%{_kernel_dir}" -name "*.ko.zst")

    # 6. Development files
    zstdmt -19 < Module.symvers > %{buildroot}%{_kernel_dir}/symvers.zst

    # Install MOK DER to kernel-specific path and to the fixed permanent path
    install -Dm644 "${MOK_DER}" "%{buildroot}%{_kernel_dir}/secureboot-meow.der"
    install -Dm644 "${MOK_DER}" "%{buildroot}/etc/kernel/certs/meow-kernel/mok.der"

    install -Dt %{buildroot}%{_devel_dir} -m644 .config Makefile Module.symvers System.map
    [ -f tools/bpf/bpftool/vmlinux.h ] && install -m644 tools/bpf/bpftool/vmlinux.h %{buildroot}%{_devel_dir}/ || true
    cp .config    %{buildroot}%{_kernel_dir}/config
    cp System.map %{buildroot}%{_kernel_dir}/System.map

    cp --parents `find -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}%{_devel_dir}
    cp -a scripts %{buildroot}%{_devel_dir}
    rm -rf %{buildroot}%{_devel_dir}/include
    rm -rf %{buildroot}%{_devel_dir}/scripts
    rm -rf %{buildroot}%{_devel_dir}/scripts/tracing
    rm -f  %{buildroot}%{_devel_dir}/scripts/spdxcheck.py

    # Files needed for `make scripts`
    cp -a --parents security/selinux/include/classmap.h              %{buildroot}%{_devel_dir}
    cp -a --parents security/selinux/include/initial_sid_to_string.h %{buildroot}%{_devel_dir}
    cp    --parents security/selinux/include/policycap.h             %{buildroot}%{_devel_dir}
    cp    --parents security/selinux/include/policycap_names.h       %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/be_byteshift.h               %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/le_byteshift.h               %{buildroot}%{_devel_dir}

    # Files needed for `make prepare` — generic
    cp -a --parents tools/bpf/resolve_btfids          %{buildroot}%{_devel_dir}
    cp -a --parents tools/build/Build.include         %{buildroot}%{_devel_dir}
    cp    --parents tools/build/fixdep.c              %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/asm                 %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/asm-generic         %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux               %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux/compiler*     %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux/types.h       %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm            %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm-generic    %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/linux          %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/vdso                %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/bpf                     %{buildroot}%{_devel_dir}
    cp    --parents tools/lib/bpf/Build               %{buildroot}%{_devel_dir}
    cp    --parents tools/lib/*.c                     %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/subcmd                  %{buildroot}%{_devel_dir}
    cp    --parents tools/objtool/*.[ch]              %{buildroot}%{_devel_dir}
    cp    --parents tools/objtool/Build               %{buildroot}%{_devel_dir}
    cp    --parents tools/objtool/include/objtool/*.h %{buildroot}%{_devel_dir}
    cp    --parents tools/objtool/sync-check.sh       %{buildroot}%{_devel_dir}
    cp    --parents tools/scripts/utilities.mak       %{buildroot}%{_devel_dir}

    # Files needed for `make prepare` — x86_64
    cp -a --parents arch/x86/boot/ctype.h                    %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.c                   %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.h                   %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl   %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl   %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/include                         %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/entry64.S             %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/purgatory.c           %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/setup-x86_64.S        %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/stack.S               %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.c                  %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.h                  %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_32.c               %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_64.c               %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_common.c           %{buildroot}%{_devel_dir}
    cp -a --parents scripts/syscallhdr.sh                    %{buildroot}%{_devel_dir}
    cp -a --parents scripts/syscalltbl.sh                    %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include/asm               %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include/uapi/asm          %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/lib/                      %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk %{buildroot}%{_devel_dir}
    cp -a --parents tools/objtool/arch/x86/                  %{buildroot}%{_devel_dir}

    # Misc headers
    cp -a include                  %{buildroot}%{_devel_dir}/include
    cp -a sound/soc/sof/sof-audio.h %{buildroot}%{_devel_dir}/sound/soc/sof
    cp -a tools/objtool/fixdep     %{buildroot}%{_devel_dir}/tools/objtool/
    cp -a tools/objtool/objtool    %{buildroot}%{_devel_dir}/tools/objtool/

    # Final cleanup
    echo "Cleaning up development files..."
    find %{buildroot}%{_devel_dir}/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    find %{buildroot}%{_devel_dir}/tools   \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    touch -r %{buildroot}%{_devel_dir}/Makefile %{buildroot}%{_devel_dir}/include/generated/uapi/linux/version.h %{buildroot}%{_devel_dir}/include/config/auto.conf

    # These symlinks are owned by the modules package; without the -devel package
    # installed they would be broken.
    rm -rf %{buildroot}%{_kernel_dir}/build
    ln -s %{_devel_dir}            %{buildroot}%{_kernel_dir}/build
    ln -s %{_kernel_dir}/build     %{buildroot}%{_kernel_dir}/source

    # Stub initramfs to inflate disk space requirements and help prevent
    # initramfs failures due to insufficient space in /boot (#bz #530778).
    echo "Creating stub initramfs..."
    install -dm755 %{buildroot}/boot
    dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{_kver}.img bs=1M count=90

# ==============================================================================
%package core
# ==============================================================================
Summary:   Linux BORE Cachy Sauce Kernel by CachyOS with other patches and improvements
AutoReq:   no

Conflicts: xfsprogs < 4.3.0-1
Conflicts: xorg-x11-drv-vmmouse < 13.0.99

Provides: installonlypkg(kernel)
Provides: kernel              = %{_rpmver}
Provides: kernel-core-uname-r = %{_kver}
Provides: kernel-uname-r      = %{_kver}

Requires:      kernel-modules-uname-r = %{_kver}
Requires(pre): /usr/bin/kernel-install
Requires(pre): coreutils
Requires(pre): dracut >= 027
Requires(pre): systemd >= 203-2
Requires(pre): ((linux-firmware >= 20150904-56.git6ebf5d57) if linux-firmware)

Requires(preun): systemd >= 200

Recommends: linux-firmware

%description core
    The kernel package contains the Linux kernel (vmlinuz), the core of any
    Linux operating system. The kernel handles the basic functions of the
    operating system: memory allocation, process allocation, device input
    and output, etc.

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
    # Remind the user to enroll the MOK key if Secure Boot is active
    if [ -f "%{_kernel_dir}/secureboot-meow.der" ]; then
        if command -v mokutil &>/dev/null; then
            SB_STATE=$(mokutil --sb-state 2>/dev/null || true)
            echo ""
            echo "======================================================================"
            echo " kernel-cachyos-meow: Secure Boot key enrollment"
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
    /etc/kernel/certs/meow-kernel/mok.der
    %{_kernel_dir}/System.map
    %{_kernel_dir}/config
    %{_kernel_dir}/modules.builtin
    %{_kernel_dir}/modules.builtin.modinfo
    %{_kernel_dir}/secureboot-meow.der
    %{_kernel_dir}/symvers.zst
    %{_kernel_dir}/vmlinuz

# ==============================================================================
%package modules
# ==============================================================================
Summary: Kernel modules package for %{name}

Provides: installonlypkg(kernel-module)
Provides: kernel-modules              = %{_rpmver}
Provides: kernel-modules-core         = %{_rpmver}
Provides: kernel-modules-core-uname-r = %{_kver}
Provides: kernel-modules-extra        = %{_rpmver}
Provides: kernel-modules-extra-uname-r = %{_kver}
Provides: kernel-modules-uname-r      = %{_kver}
Provides: v4l2loopback-kmod           = 0.14.0

Requires: kernel-uname-r = %{_kver}

%if %{_build_lto}
Requires: clang llvm llvm-devel lld
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
    %{_kernel_dir}/build
    %{_kernel_dir}/kernel
    %{_kernel_dir}/modules.order
    %{_kernel_dir}/source

# ==============================================================================
%package devel
# ==============================================================================
Summary:     Development package for building kernel modules to match %{name}
AutoReqProv: no

Provides: installonlypkg(kernel)
Provides: kernel-devel          = %{_rpmver}
Provides: kernel-devel-uname-r  = %{_kver}

Requires(pre): findutils
Requires:      bison
Requires:      elfutils-libelf-devel
Requires:      findutils
Requires:      flex
Requires:      make
Requires:      openssl-devel
Requires:      perl-interpreter

%if %{_build_lto}
Requires: clang
Requires: lld
Requires: llvm
%else
Requires: gcc
%endif

%description devel
    This package provides kernel headers and makefiles sufficient to build
    modules against %{name}.

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

# ==============================================================================
%package devel-matched
# ==============================================================================
Summary: Meta package to install matching core and devel packages for %{name}

Provides: kernel-devel-matched = %{_rpmver}

Requires: %{name}-core  = %{_rpmver}
Requires: %{name}-devel = %{_rpmver}

%description devel-matched
    This meta package is used to install matching core and devel packages
    for %{name}.

%files devel-matched

# ==============================================================================
%if %{_build_nv}
%package nvidia-open
# ==============================================================================
Summary: nvidia-open %{_nv_ver} kernel modules for %{name}

Provides: installonlypkg(kernel-module)
Provides: nvidia-kmod >= %{_nv_ver}

Requires: kernel-uname-r  = %{_kver}
Requires: nvidia-gpu-firmware

Conflicts: akmod-nvidia

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

# ==============================================================================
%files
