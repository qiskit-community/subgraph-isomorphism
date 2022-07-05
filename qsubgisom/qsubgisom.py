# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Implementation of the functions for the construction of the Quantum Subgraph Isomorphism
algorithm."""

from itertools import chain
from typing import Union, Tuple
import numpy as np
from qiskit import QuantumRegister, QuantumCircuit, opflow
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import Diagonal


IntOrTuple = Union[int, Tuple]


def _hcph(phi: float, qc: QuantumCircuit, qubits: IntOrTuple):
    ctrl, target = qubits if isinstance(qubits, tuple) else (-1, qubits)
    qc.h(target)
    if ctrl >= 0:
        qc.cp(phi, ctrl, target)
    else:
        qc.p(phi, target)
    qc.h(target)


S4_BLOCK_PARCOUNT = 5


def _s4_block(params: np.ndarray) -> QuantumCircuit:
    """Build the basic block S4 for the permutations Ansatz.

    Args:
        params (np.ndarray): The array of parameters.
    """
    params = np.asarray(params).flatten()
    assert params.shape == (S4_BLOCK_PARCOUNT,)
    qc = QuantumCircuit(QuantumRegister(name="q", size=2))
    _hcph(params[0], qc, 0)

    qc.h(1)
    qc.p(params[1], 1)
    qc.cp(params[2], 0, 1)
    qc.h(1)

    _hcph(params[3], qc, (1, 0))
    _hcph(params[4], qc, (0, 1))
    return qc


def _map_qreg(array, qreg: QuantumRegister) -> np.ndarray:
    assert isinstance(qreg, QuantumRegister)
    array = np.asarray(array)
    fun = np.vectorize(lambda i: qreg[i])
    return fun(array)


def _expand_topology(topology, *, qreg: QuantumRegister) -> np.ndarray:
    if isinstance(topology, str):
        if topology in {"linear", "circular"}:
            v = np.arange(qreg.size - 1)
            v = np.stack([v, v + 1]).T
            if topology == "circular" and qreg.size > 2:
                v = np.concatenate([v, np.array([[qreg.size - 1, 0]])], axis=0)
            topology = v
        else:
            raise ValueError(f"Unrecognized topology: {topology}")
    topology = np.asarray(topology)
    assert topology.ndim == 2 and topology.shape[1] == 2
    return _map_qreg(topology, qreg=qreg)


def s4_ansatz(
    topology, *, qreg: Union[QuantumRegister, int], params=None
) -> Tuple[QuantumCircuit, np.ndarray]:
    """Construct the permutations ansatz based on the S4 block.

    Args:
        topology (str, np.ndarray): The topology for the ansatz, see the function
        ansatz() for more information.
        qreg (QuantumRegister, int): The destination quantum register.
        params (np.ndarray): The array of parameters.
    """
    if isinstance(qreg, int):
        qreg = QuantumRegister(qreg)
    assert isinstance(qreg, QuantumRegister)
    topology = _expand_topology(topology, qreg=qreg)
    if params is None:
        params = params_tensor((len(topology), S4_BLOCK_PARCOUNT))
    params = np.asarray(params)
    assert params.ndim == 2 and params.shape[1] == S4_BLOCK_PARCOUNT
    assert len(params) == len(topology)
    qc = QuantumCircuit(qreg)
    for v, q in zip(params, topology):
        qc.compose(_s4_block(v), qubits=q, inplace=True)

    qc_ = QuantumCircuit(qreg)
    qc_.compose(qc.to_gate(label="PermAnsatz"), inplace=True)
    return qc_, params


def params_tensor(shape, *, name="t") -> np.ndarray:
    """Prepare a tensor of circuit parameters."""
    shape = tuple(np.atleast_1d(shape).flatten())
    v = ParameterVector(name=name, length=np.product(shape))
    v = np.array(v.params, dtype=np.object)
    return v.reshape(shape)


def observable(n: int) -> opflow.OperatorBase:
    """Prepare the observable for the VQE Framework."""
    obs0 = (opflow.Z + opflow.I) / 2
    return -obs0.tensorpower(n)


def _is_pow_2(v: int):
    assert isinstance(v, int)
    return (bin(v).count("1") == 1) or (v == 0)


def _pow2_shaped_mat_validation(mat):
    mat = np.asarray(mat)
    assert mat.ndim == 2
    assert mat.shape[0] == mat.shape[1]
    assert all(map(_is_pow_2, mat.shape))
    return mat


def _circ_qregs(n: int, *, as_qubits=False):
    assert (n + 1) % 2 == 0
    m = (n - 1) // 2
    regs_config = zip((m, m, 1), ("i", "j", "a"))
    ret = tuple(QuantumRegister(sz, name=name) for sz, name in regs_config)
    return tuple(chain(*ret)) if as_qubits else ret


def _adj_flatten_repr(adj: np.ndarray, *, shape=None) -> QuantumCircuit:
    """Produce the quantum circuit that represents the given
    adjacency matrix in flattened form as diagonal operator.

    Args:
        adj: The input adjacency matrix.
        shape: Optional shape for the input matrix. When not None
        the input matrix is zero-padded extended to this shape.
    """
    adj = np.round(adj) != 0
    assert adj.ndim == 2 and adj.shape[0] == adj.shape[1]
    adj = adj if shape is None else _mat_zero_ext(adj, shape=shape)
    assert _is_pow_2(len(adj))
    adj = adj.flatten()
    adj = np.concatenate([np.zeros_like(adj), adj])
    adj = np.exp(1j * adj * np.pi)
    adj = Diagonal(adj)
    qc = QuantumCircuit(*_circ_qregs(adj.num_qubits))
    qc = qc.compose(
        adj.to_gate(label="QAdj"), qubits=_circ_qregs(adj.num_qubits, as_qubits=True)
    )
    return qc


def _mat_zero_ext(mat, *, shape):
    mat = np.asarray(mat)
    ret = np.zeros(shape, dtype=mat.dtype)
    ret[: mat.shape[0], : mat.shape[1]] = mat
    return ret


def _qc_block(qc, label=None):
    qc_ = QuantumCircuit(*qc.qregs, *qc.cregs)
    qc_.compose(qc.to_gate(label=label), inplace=True)
    return qc_


def ansatz(adj1, adj2, *, topology="circular") -> Tuple[QuantumCircuit, np.ndarray]:
    """Construct the quantum circuit for the ansatz depending on the
    input adacency matrices.

    Args:
        adj1 (np.ndarray): The adjacency matrix of the input graph. The input graph must
            have at least the same number of vertices as the pattern graph.
        adj2 (np.ndarray): The eadjacency matrix of the pattern graph.
        topology (str, list): The topology for the ansatz. This can be either a string
            naming a pre-defined topology such as "circular" or "linear",
            or a list of tuples where each tuple represent an entangling pair.
    """
    adj1, adj2 = map(_pow2_shaped_mat_validation, (adj1, adj2))
    assert len(adj2) <= len(adj1)
    gisom = adj1.shape == adj2.shape

    qc = _adj_flatten_repr(adj1)
    qregs = _circ_qregs(qc.num_qubits)

    h_layer = QuantumCircuit(*qregs)
    n = int(np.log2(len(adj2)))
    for r in qregs[:2]:
        h_layer.h(r[:n])
    h_layer.h(qregs[2])

    perm_qc, params = s4_ansatz(topology, qreg=qregs[0])
    if not gisom:
        qc.compose(
            _qc_block(perm_qc.inverse(), label="PermAnsatzDg"),
            front=True,
            inplace=True,
            qubits=qregs[0],
        )
        qc.compose(
            _qc_block(perm_qc.inverse(), label="PermAnsatzDg"),
            front=True,
            inplace=True,
            qubits=qregs[1],
        )
    qc.compose(h_layer, front=True, inplace=True)
    qc.compose(perm_qc, inplace=True, qubits=qregs[0])
    qc.compose(perm_qc, inplace=True, qubits=qregs[1])
    qc.compose(_adj_flatten_repr(adj2, shape=adj1.shape), inplace=True)
    qc.compose(h_layer, inplace=True)
    return qc, params


def thetas_to_prob(x) -> np.ndarray:
    """Transform an array of angles into an array of probabilities.
    The probabilities are obtained by considering how close
    is each angle to an even or odd multiple of pi.
    """
    x = np.asarray(x) / np.pi
    x = np.abs(x)
    r = np.modf(x)
    r = r[0], r[1] % 2
    return np.abs(r[0] - r[1])


def sample_exact_thetas(v, *, n=1, seed=None):
    """Given the values of the parameters for the ansatz,
    sample a configuration for the same parameters such that
    the ansatz implements a single permutation and there is
    a notion of closeness with respect to the input parameters.

    Args:
        v (np.ndarray): The array of parameters.
        n (int): The number of samples to be drawn.
        seed (None, int): Optional seed for the random number generator.
    """
    if isinstance(v, dict):
        dkeys = v.keys()
        v = np.array(list(v.values()))
    v = thetas_to_prob(v)
    rng = np.random.default_rng(seed)
    prob = rng.uniform(size=(n, len(v)))
    v = (prob < v) * np.pi
    if dkeys is not None:
        v = [dict(zip(dkeys, v1)) for v1 in v]
        assert len(v) == n
    return v


def perm_to_2line(mat, *, inverse=False) -> np.ndarray:
    """Convert a permutation matrix to a two line symbol.

    Args:
        mat (np.ndarray): The input permutation matrix.
        inverse (bool): When True return the two line symbol corresponding
        to the inverse of the permutation.
    """
    mat = np.stack(np.nonzero(mat))
    mat = mat if inverse else mat[::-1]
    return mat[:, np.argsort(mat[0])]
