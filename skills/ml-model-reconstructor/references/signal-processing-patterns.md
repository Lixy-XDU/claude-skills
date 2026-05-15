# Signal Processing Pattern Mapping

## Discrete signals and indexing

MATLAB arrays are one-based, but mathematical signal notation is usually zero-based. State the convention explicitly:

- Code index `x(k)` often maps to `x[k-1]`.
- If formulas in code use `k` as a physical time index, preserve that convention and explain it.
- Time vector patterns:
  - `t = (0:N-1)/fs` implies `t_n = n/f_s`.
  - `dt` or `Ts` implies `t_n = nT_s` and `f_s = 1/T_s`.

## FFT and spectra

MATLAB DFT convention:

```latex
X[k] = \sum_{n=0}^{N-1} x[n] e^{-j2\pi kn/N}
```

Inverse convention:

```latex
x[n] = \frac{1}{N}\sum_{k=0}^{N-1} X[k] e^{j2\pi kn/N}
```

Common code mappings:

- `fft(x,N)` → N-point DFT, zero-padding or truncation depending on `N`.
- `abs(fft(x))/N` → amplitude-normalized spectrum.
- one-sided scaling `P1(2:end-1)=2*P1(2:end-1)` → real-signal one-sided amplitude spectrum.
- `fftshift` → centered frequency axis, usually `[-fs/2, fs/2)`.
- `pwelch`, `periodogram`, `spectrogram` → PSD or time-frequency estimate; include window, overlap, FFT length, and scaling.

## Filters

For `y = filter(b,a,x)`, reconstruct:

```latex
\sum_{r=0}^{N_a} a_r y[n-r] = \sum_{m=0}^{N_b} b_m x[n-m],\quad a_0=1
```

Transfer function:

```latex
H(z)=\frac{\sum_{m=0}^{N_b} b_m z^{-m}}{\sum_{r=0}^{N_a} a_r z^{-r}}
```

For FIR filters where `a = 1`:

```latex
y[n]=\sum_{m=0}^{M} b_m x[n-m]
```

For `filtfilt`, state that forward-backward filtering cancels phase under standard assumptions and squares the magnitude response.

## Convolution and correlation

- `conv(x,h)` → linear convolution: `y[n]=\sum_k x[k]h[n-k]`.
- `xcorr(x,y)` → cross-correlation; verify MATLAB's lag convention.
- FFT-based convolution usually implies circular convolution unless zero-padding length is at least `length(x)+length(h)-1`.

## Estimation and detection

- Matched filter: convolution/correlation with a reversed conjugate template.
- Least-squares spectral fitting: map design matrix rows to basis functions.
- Adaptive filters: identify update rule, error signal, step size, and stability assumptions.
