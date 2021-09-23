from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import QasmSimulator

def simulate(qc, shots=1024):
  """Simulates the given circuit and returns the counts from the results"""
  simulator = QasmSimulator()
  compiled_circuit = transpile(qc, simulator)
  job = simulator.run(compiled_circuit, shots=shots)
  result = job.result()
  counts = result.get_counts(qc)
  return counts

def one_hot_fan(base, fan, qc=None):
  """
  Creates a one-hot encoding instruction, using fanout, from base to fan.
  @param qc: If qc is supplied, the encoding will be applied directly to qc. 
  """
  encoder = QuantumCircuit(base, fan, name="one_hot") if qc is None else qc

  encoder.x(fan[0])
  #do first iteration manually
  encoder.cnot(base[0], fan[1])
  encoder.cnot(fan[1], fan[0])
  
  for i in range(1,base.size):
    for j in range(2**i):
      #write
      encoder.ccx(base[i],fan[j], fan[2**i + j])
    for j in range(2**i):
      #correct
      encoder.cnot(fan[2**i + j], fan[j])
  
  return encoder.to_instruction() if qc is None else None

def controlled_read(control, mem, block_size, output, qc=None):
  """Creates a controlled read where each item is conditionally read
  from mem to output, based on control.
  @param qc: If qc is supplied, the read will be applied directly to qc.
  """
  circ = QuantumCircuit(control, mem, output, name="c-read") if qc is None else qc

  #for each target bit, block
  for i in range(len(control)):
    #read each bit in the block
    for j in range(block_size):
      loc = i*block_size + j
      # circ.ccx(control[i], mem[loc], output[loc])
      circ.ccx(control[i], mem[loc], output[j])

  return circ.to_instruction() if qc is None else None

def spread(registers):
  """Flattens the array of registers into one array of bits.
  """
  res = []
  for reg in registers:
    for bit in reg:
      res.append(bit)

  return res

def set_mem(values, mem, block_size, qc=None):
  """
  Reads values into the mem registers.
  @param qc: If qc is supplied, instructions are applied directly to the circuit.
  """
  mem_set = QuantumCircuit(mem, name="set-mem") if qc is None else qc

  for i,value in enumerate(values):
    binary = [int(bit) for bit in bin(value)[2:]]
    #pad binary with any leading 0s.
    diff = block_size-len(binary)
    binary = [0]*diff + binary

    #need to reverse so that least sig bit is first
    for j, bit in enumerate(binary[::-1]):
      if bit == 1:
        mem_set.x(mem[i*block_size + j])

  return mem_set.to_instruction() if qc is None else None
