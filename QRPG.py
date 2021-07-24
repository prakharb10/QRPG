from qiskit import QuantumRegister, execute, QuantumCircuit, IBMQ, Aer
from qiskit.providers.ibmq import least_busy
from qiskit.providers.ibmq.exceptions import IBMQAccountError
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram
import streamlit as st

st.set_page_config(page_title='Quantum Random Password Generator')
st.title('Quantum Random Password Generator')
st.header('Using Qiskit and IBMQ')
st.subheader('by Prakhar Bhatnagar')

st.text_area('What is this project?',
             value='A program to generate truly random numbers using real Quantum Computers and then generate a password using them.')

backend_choice = st.radio('Choose a backend', ('Simulator', 'IBMQ Device'))


@st.cache(suppress_st_warning=True)
def loadAccount(token):
    try:
        IBMQ.enable_account(token)
    except IBMQAccountError:
        try:
            IBMQ.load_account()
        except:
            st.error('Error occured while loading IBMQ Account')
        else:
            st.success('Loaded account successfully!')
    except:
        st.error('Error occured while loading IBMQ Account')
    else:
        st.success('Loaded account successfully!')


if backend_choice == 'IBMQ Device':
    st.info(
        'To run the program on a real Quantum Computer, you have to enter your IBMQ Account Token which can be found on the Account Page of your IBM Quantum Experience Account.')
    account_token = st.text_input('IBMQ Account Token')
    st.info(
        'NOTE: Running the task on a real quantum computer may take upto several minutes depending on the job queue')
    if account_token != "":
        loadAccount(account_token)

pass_length = st.slider('Password Length', min_value=4,
                        max_value=12, value=8, step=2)
clicked = st.button("Generate")


def getBackend():
    provider = IBMQ.get_provider(hub='ibm-q')
    backendd = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= 5
                                                              and not x.configuration().simulator
                                                              and x.status().operational == True))
    st.write('Backend Chosen: ', backendd.name())
    return backendd


# TODO: try caching this
with st.echo():
    def circuit():
        q = QuantumRegister(5, 'q')
        circuit = QuantumCircuit(q)
        circuit.h(q)
        circuit.measure_all()
        return circuit


def job_state_print(job_id, job_status, job, queue_info):
    print(job_status)
    st.write(job_status)


# TODO: Show job status
def run_job(circ, sht):
    if backend_choice == 'IBMQ Device':
        bk = getBackend()
    else:
        bk = Aer.get_backend('qasm_simulator')
    job = execute(circ, backend=bk, shots=int(sht))
    job.wait_for_final_state(callback=job_state_print)
    # job_monitor(job)
    counts = job.result().get_counts()
    ccounts = counts.copy()
    for i in list(counts):
        counts[int(str(i), 2)] = counts[i]
        del counts[i]
    st.write(plot_histogram(counts, title='Job Result', figsize=(10, 5)))
    st.balloons()
    bintoASCII(ccounts)


def bintoASCII(count):
    password = ''
    for i in list(count):
        for j in range(count[i]):
            if int(str(i)[-2:], 2) == 1:
                num = int(str(i), 2) + 32
                if num == 32:
                    num += 1
            elif int(str(i)[-2:], 2) == 3:
                num = int(str(i), 2) + 96
                if num == 127:
                    num -= 1
            else:
                num = int(str(i), 2) + 64
            char = chr(num)
            password += char
    st.title(password)


if clicked:
    c = circuit()
    st.write(c.draw(output='mpl', interactive=True))
    st.caption('Quantum Circuit')
    run_job(c, pass_length)
    clicked = not clicked
