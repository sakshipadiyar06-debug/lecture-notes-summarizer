"""
Generates a realistic multi-page university lecture PDF using ReportLab
for testing the PDF extraction and summarization pipeline.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def build_lecture_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#053A41'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1C7C84'),
        spaceAfter=14
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#044F58'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        leftIndent=18,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4
    )

    story = []

    # Title & Header
    story.append(Paragraph("PHYS 405: Quantum Computing and Information Theory", title_style))
    story.append(Paragraph("Lecture 7: Qubits, Superposition, Entanglement, and Quantum Gates | Prof. Richard Thorne", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#FC931F'), spaceAfter=14))

    # Section 1
    story.append(Paragraph("1. Foundational Quantum Mechanics and the Qubit", h2_style))
    story.append(Paragraph(
        "In classical computing, information is fundamentally physical and discrete: a transistor is either on or off, "
        "representing a deterministic state of 0 or 1. In quantum computing, however, the fundamental unit of information "
        "is the quantum bit, or qubit. A qubit is a two-level quantum mechanical system described mathematically as a state "
        "vector in a two-dimensional complex Hilbert space.",
        body_style
    ))
    story.append(Paragraph(
        "Unlike a classical bit, a qubit can exist in a linear combination of both basis states simultaneously, known as "
        "superposition. We express an arbitrary pure state as: |psi> = alpha |0> + beta |1>, where alpha and beta are complex "
        "probability amplitudes. According to the Born rule, upon measurement in the computational basis, the qubit collapses "
        "to state |0> with probability |alpha|^2 and to state |1> with probability |beta|^2, with the normalization condition "
        "requiring |alpha|^2 + |beta|^2 = 1.",
        body_style
    ))

    # Section 2
    story.append(Paragraph("2. Multi-Qubit Registers and Quantum Superposition Scaling", h2_style))
    story.append(Paragraph(
        "The computational power of quantum systems emerges when we consider multi-qubit systems. When two independent "
        "qubits are combined, their composite state space is formed via the tensor product of their individual Hilbert spaces. "
        "For an n-qubit quantum register, the state vector resides in a 2^n dimensional Hilbert space.",
        body_style
    ))
    story.append(Paragraph("Key properties of multi-qubit superposition include:", body_style))
    story.append(Paragraph("&bull; <b>Exponential Representation</b>: An n-qubit system simultaneously maintains 2^n complex amplitudes.", bullet_style))
    story.append(Paragraph("&bull; <b>Quantum Parallelism</b>: Unitary operations act simultaneously on all basis states in superposition.", bullet_style))
    story.append(Paragraph("&bull; <b>Interference</b>: Quantum algorithms manipulate probability amplitudes so constructive interference amplifies correct solutions while destructive interference cancels incorrect ones.", bullet_style))

    # Section 3
    story.append(Paragraph("3. Quantum Entanglement and Non-Locality", h2_style))
    story.append(Paragraph(
        "Quantum entanglement represents a profound departure from classical physics. A multi-qubit state is entangled if it "
        "cannot be factored into the tensor product of its individual constituent qubit states. The four maximally entangled "
        "two-qubit states are known as the Bell States or EPR pairs. The canonical Bell state is: "
        "|Phi+> = (1 / sqrt(2)) * (|00> + |11>).",
        body_style
    ))
    story.append(Paragraph(
        "If Alice and Bob share an entangled pair |Phi+>, measuring Alice's qubit instantly collapses Bob's qubit into the identical "
        "value, regardless of the physical distance separating them. This non-local correlation forms the backbone of quantum "
        "key distribution (QKD), quantum teleportation, and superdense coding.",
        body_style
    ))

    # Section 4
    story.append(Paragraph("4. Unitary Quantum Gates and Circuit Topologies", h2_style))
    story.append(Paragraph(
        "All quantum logic operations (excluding measurement) must be strictly reversible and norm-preserving, governed by "
        "unitary transformation matrices U where U_dagger * U = I. Critical single-qubit gates include:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Pauli-X Gate</b>: The quantum NOT gate, flipping |0> to |1> and |1> to |0>.", bullet_style))
    story.append(Paragraph("&bull; <b>Hadamard Gate (H)</b>: Creates equal superpositions, mapping |0> to (|0>+|1>)/sqrt(2).", bullet_style))
    story.append(Paragraph("&bull; <b>Phase Shift Gate (S/T)</b>: Modifies the relative phase of the |1> component without affecting probabilities.", bullet_style))
    story.append(Paragraph("&bull; <b>Controlled-NOT (CNOT)</b>: A two-qubit entangling gate that inverts the target qubit if the control qubit is |1>.", bullet_style))

    # Section 5
    story.append(Paragraph("5. Decoherence and the Threshold Theorem", h2_style))
    story.append(Paragraph(
        "The primary obstacle preventing large-scale fault-tolerant quantum computing is environmental decoherence. Unwanted "
        "interactions between qubits and thermal, magnetic, or electromagnetic environmental fluctuations destroy fragile "
        "phase coherence. Relaxation time T1 and dephasing time T2 quantify qubit longevity. Practical fault-tolerance relies "
        "on Quantum Error Correction (QEC) codes, such as the Surface Code, which encode a single logical qubit across an array "
        "of entangled physical data and syndrome qubits.",
        body_style
    ))

    doc.build(story)
    print(f"Successfully generated PDF: {output_path}")


if __name__ == "__main__":
    out_pdf = Path(__file__).parent / "sample_lectures" / "quantum_computing_lecture.pdf"
    build_lecture_pdf(str(out_pdf))
