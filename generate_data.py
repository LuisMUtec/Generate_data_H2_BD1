#!/usr/bin/env python3
"""
generate_data.py

Genera datos sintéticos para las tablas:
  Persona, Paciente, Especialidad, Medico, Cabina,
  Personal, Turno y Cita

Cada tabla tendrá el mismo número de filas, indicado con --datos.

Requiere:
    pip install faker

Uso:
    python generate_data.py --datos 100000
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def random_time():
    h = random.randint(8, 18)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    parser = argparse.ArgumentParser(
        description="Genera datos sintéticos para todas las tablas.")
    parser.add_argument(
        '--datos', type=int, required=True,
        help='Número de filas a generar en cada tabla')
    args = parser.parse_args()

    N = args.datos
    fake = Faker()  # locale por defecto (en_US)

    # 1) Persona
    with open('persona.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'id_persona','nombre','apellido','dni',
            'fecha_nacimiento','sexo','correo','telefono'
        ])
        for pid in range(1, N+1):
            dob = random_date(
                datetime(1940,1,1).date(),
                datetime(2005,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                pid,
                fake.first_name(),
                fake.last_name(),
                fake.unique.random_number(digits=8, fix_len=True),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone
            ])

    # 2) Paciente
    with open('paciente.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_paciente','id_persona','tipo_seguro','fecha_registro'])
        for i in range(1, N+1):
            w.writerow([
                i,
                random.randint(1, N),
                random.choice(['SIS','Essalud','Privado','Ninguno']),  # Fixed: Changed 'Particular' to 'Ninguno'
                random_date(
                    datetime(2020,1,1).date(),
                    datetime(2025,6,28).date()
                )
            ])

    # 3) Especialidad
    with open('especialidad.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_especialidad','nombre','descripcion'])
        for eid in range(1, N+1):
            w.writerow([
                eid,
                f"Especialidad_{eid}",
                fake.sentence(nb_words=6)
            ])

    # 4) Medico
    with open('medico.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_medico','id_persona','id_especialidad'])
        for i in range(1, N+1):
            w.writerow([
                i,
                random.randint(1, N),
                random.randint(1, N)
            ])

    # 5) Cabina
    with open('cabina.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_cabina','numero','ubicacion'])
        for cid in range(1, N+1):
            w.writerow([
                cid,
                f"C{cid:03d}",
                fake.city()
            ])

    # 6) Personal
    with open('personal.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_personal','id_persona','rol'])
        for i in range(1, N+1):
            w.writerow([
                i,
                random.randint(1, N),
                random.choice(['Recepcionista','Enfermero','Administrador'])
            ])

    # 7) Turno - Fixed: Added 'fecha' column and changed turno values to lowercase
    with open('turno.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_personal','id_cabina','fecha','turno'])  # Added 'fecha' column
        for i in range(1, N+1):
            w.writerow([
                random.randint(1, N),
                random.randint(1, N),
                random_date(  # Added fecha field
                    datetime(2024,1,1).date(),
                    datetime(2025,12,31).date()
                ),
                random.choice(['mañana','tarde','noche'])  # Changed to lowercase to match CHECK constraint
            ])

    # 8) Cita - Fixed: Changed 'atendida' to 'confirmada' to match CHECK constraint
    with open('cita.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'id_cita','id_paciente','id_medico',
            'fecha','hora','estado','id_personal_registro'
        ])
        for cid in range(1, N+1):
            w.writerow([
                cid,
                random.randint(1, N),
                random.randint(1, N),
                random_date(
                    datetime(2024,1,1).date(),
                    datetime(2025,6,28).date()
                ),
                random_time(),
                random.choice(['pendiente','confirmada','cancelada','atendida']),  # Fixed: matches CHECK constraint
                random.randint(1, N)
            ])

    print(f"Archivos CSV generados con {N} filas cada uno.")

if __name__ == '__main__':
    main()

# docker run --name mi-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=hito2 -p 5555:5432 -d postgres