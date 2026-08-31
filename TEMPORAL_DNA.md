# Shared Temporal DNA

## Mathematical contract

Let `T` be the authoritative temporal metric and `N` the transition/order count.

\[
N \not\Rightarrow T
\]

Transition structure can establish ordering without uniquely determining duration.

The falsifying construction is:

\[
N_A=N_B,\qquad T_A\ne T_B
\]

and the converse:

\[
T_A=T_B,\qquad N_A\ne N_B.
\]

A frozen system has `N=0`. This establishes only that no new temporal information is produced by transitions; it does not establish that physical time ceases to exist.

## Rolling bounds

Represent temporal knowledge independently as:

\[
L\le T\le U
\]

where bounds are advanced by the authoritative temporal source rather than derived from transition count.

## Engineering invariant

`transition_count` is observational/order metadata. It must never be treated as the authoritative clock or as a unique conversion to elapsed duration.

## Shared/split architecture

`the-clock` and `osu!megamix` share this mathematical DNA while retaining independent temporal implementations.

This is a computational/modeling result, not a claim that physics has experimentally established the ontology of time.
STRING → pulls time forward | NAIL → creates the current temporal instant (TI)
