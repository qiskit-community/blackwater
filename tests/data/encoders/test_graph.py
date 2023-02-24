"""Test graph encoders."""
from unittest import TestCase

from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import FakeLimaV2

from blackwater.data.encoders.graph import circuit_to_json_graph, backend_to_json_graph, GraphData
from blackwater.data.encoders.node_encoder import BackendNodeEncoder


def create_bell_circuit(num_qubits: int = 2, insert_barriers: bool = False) -> QuantumCircuit:
    circuit = QuantumCircuit(num_qubits)
    circuit.h(0)
    if insert_barriers:
        circuit.barrier(0)
    for i in range(num_qubits - 1):
        circuit.cx(i, i + 1)
    if insert_barriers:
        circuit.barrier()
    circuit.measure_all()
    return circuit


class TestGraphEncoders(TestCase):
    """TestGraphEncoders."""

    def test_circuit_encoder_base(self):
        """Tests circuit encoder."""
        circuit = create_bell_circuit()

        encoded_circuit_json = circuit_to_json_graph(circuit, available_instructions=["h", "cx"])
        expecting = GraphData(
            nodes=[
                [1, 0, 0, 0, 0, 0.0, 0.0, 0.0],
                [0, 1, 0, 0, 0, 0.0, 0.0, 0.0],
                [0, 0, 1, 0, 0, 0.0, 0.0, 0.0],
                [0, 0, 0, 1, 0, 0.0, 0.0, 0.0],
                [0, 0, 0, 1, 0, 0.0, 0.0, 0.0]
            ],
            edges=[[0, 1], [1, 2], [1, 2], [2, 4], [2, 3]]
        )
        self.assertEqual(expecting, encoded_circuit_json)

    def test_circuit_encoder_with_node_backend_encoder(self):
        """Tests circuit encoding with Backend node encoder."""
        circuit = create_bell_circuit(3, insert_barriers=True)
        fake_lima = FakeLimaV2()

        transpiled_circuit = transpile(circuit, fake_lima)

        backend_node_encoder = BackendNodeEncoder(fake_lima)
        encoded_circuit_json = circuit_to_json_graph(
            transpiled_circuit,
            node_encoder=backend_node_encoder
        )
        self.assertIsInstance(encoded_circuit_json, GraphData)
        self.assertEqual(len(encoded_circuit_json.nodes), 11)
        self.assertEqual(len(encoded_circuit_json.edges), 14)
        self.assertEqual(len(encoded_circuit_json.nodes[0]), 27)

    def test_backend_encoder_base(self):
        """Tests backend encoding."""
        fake_lima = FakeLimaV2()

        encoded_backend_json = backend_to_json_graph(fake_lima)
        self.assertIsInstance(encoded_backend_json, GraphData)
        self.assertEqual(len(encoded_backend_json.nodes), 5)
        self.assertEqual(len(encoded_backend_json.edges), 8)
