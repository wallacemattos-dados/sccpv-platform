from datetime import date
from typing import List, Optional
from sqlmodel import Session, select
from src.models import ResearchAssignment, VehicleCapture, AssignmentStatus, User, Store

class AssignmentService:
    def __init__(self, session: Session):
        self.session = session

    # --- AGENDAMENTO (Uso do Coordenador) ---
    def create_assignment(self, researcher_id: int, store_id: int, week_date: date) -> ResearchAssignment:
        """Cria uma tarefa de visita para um pesquisador."""
        assignment = ResearchAssignment(
            researcher_id=researcher_id,
            store_id=store_id,
            week_start_date=week_date,
            status=AssignmentStatus.OPEN
        )
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def get_all_assignments(self) -> List[ResearchAssignment]:
        return self.session.exec(select(ResearchAssignment)).all()

    # --- COLETA (Uso do Pesquisador) ---
    def get_my_pending_assignments(self, user_id: int) -> List[ResearchAssignment]:
        """Retorna visitas em aberto para o usuário logado."""
        return self.session.exec(
            select(ResearchAssignment)
            .where(ResearchAssignment.researcher_id == user_id)
            .where(ResearchAssignment.status == AssignmentStatus.OPEN)
        ).all()

    def capture_price(self, assignment_id: int, model_id: int, price: float, year: int) -> VehicleCapture:
        """Registra o preço de um carro na visita."""
        capture = VehicleCapture(
            assignment_id=assignment_id,
            model_id=model_id,
            price=price,
            model_year=year,
            manufacture_year=year, # Simplificação para MVP
            options=[]
        )
        self.session.add(capture)
        self.session.commit()
        return capture

    def complete_assignment(self, assignment_id: int):
        """Finaliza a visita."""
        assignment = self.session.get(ResearchAssignment, assignment_id)
        if assignment:
            assignment.status = AssignmentStatus.COMPLETED
            self.session.add(assignment)
            self.session.commit()