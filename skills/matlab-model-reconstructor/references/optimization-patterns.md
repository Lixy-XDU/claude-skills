# Optimization Pattern Mapping

## Solver-to-model mapping

### fmincon

Canonical form:

```latex
\min_x f(x)\quad
\text{s.t.}\quad A x \le b,\ A_{eq}x=b_{eq},\ lb\le x\le ub,\ c(x)\le 0,\ c_{eq}(x)=0
```

Map from code:

- objective handle: `fun`, `@(x) ...`
- initial guess: `x0`
- linear constraints: `A,b,Aeq,beq`
- bounds: `lb,ub`
- nonlinear constraints: `nonlcon`
- options: algorithm, tolerances, gradients

### quadprog

Canonical form:

```latex
\min_x \frac{1}{2}x^T Hx + f^T x
```

with the same linear constraints and bounds as above. Check whether `H` is symmetric positive semidefinite before claiming convexity.

### linprog

```latex
\min_x f^T x
```

subject to linear constraints and bounds.

### lsqnonlin / lsqcurvefit

Residual form:

```latex
\min_x \frac{1}{2}\|r(x)\|_2^2
```

For linear residual `r(x)=Ax-y`, derive normal equations only when appropriate:

```latex
A^T A x = A^T y
```

State rank and conditioning assumptions.

## Custom iterative algorithms

### Gradient descent

Code patterns: `x = x - alpha*g`, `grad`, finite differences.

```latex
x_{k+1}=x_k-\alpha_k\nabla f(x_k)
```

Include step-size schedule, stopping rule, and convergence assumptions only if supported.

### Projected gradient

Code patterns: `min(max(x,lb),ub)`, projection, clipping.

```latex
x_{k+1}=\Pi_{\mathcal C}(x_k-\alpha_k\nabla f(x_k))
```

### ADMM / augmented Lagrangian

Look for variables such as `rho`, `lambda`, `dual`, `z`, `u` and alternating updates. Reconstruct primal objective, splitting variables, augmented term, and dual update.

## Constraint reconstruction

- `A*x <= b` or manually computed inequalities imply feasibility constraints.
- Penalized violations, e.g. `max(0,g(x)).^2`, may represent soft constraints rather than hard constraints.
- Normalization operations can imply simplex, unit-norm, probability, or energy constraints; state which is supported by context.

## KKT derivation checklist

Derive KKT conditions only after identifying:

1. decision variable domain,
2. differentiable objective,
3. equality constraints,
4. inequality constraints,
5. constraint qualification assumptions.

For inequality constraints `g_i(x) <= 0`, use:

```latex
\nabla f(x^*) + \sum_i \lambda_i \nabla g_i(x^*) + \sum_j \nu_j \nabla h_j(x^*) = 0,
\quad \lambda_i \ge 0,
\quad \lambda_i g_i(x^*)=0
```
