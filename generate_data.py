#!/usr/bin/env python3
"""
generate_data.py

Genera datos sintéticos para las tablas del nuevo esquema:
  Paciente, Especialidad, Medico, Medico_Especialidad, Cabina,
  Consultorio, Personal, Turno y Cita

Cada tabla tendrá el mismo número de filas, indicado con --datos.

Requiere:
    pip install faker

Uso:
    python generate_data.py --datos 100000
"""

import argparse
import csv
import os
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

def generate_dni():
    """Genera un DNI de 8 dígitos"""
    return f"{random.randint(10000000, 99999999)}"

def main():
    parser = argparse.ArgumentParser(
        description="Genera datos sintéticos para todas las tablas.")
    parser.add_argument(
        '--datos', type=int, required=True,
        help='Número de filas a generar en cada tabla')
    args = parser.parse_args()

    N = args.datos
    fake = Faker()  # locale por defecto (en_US)

    # Crear directorio basado en el número de datos
    output_dir = f"datos_{N}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generando datos en el directorio: {output_dir}/")

    # Listas para almacenar los DNIs generados
    pacientes_dni = []
    medicos_dni = []
    personal_dni = []
    especialidades = []
    cabinas = []
    consultorios = []

    # 1) Paciente
    with open(os.path.join(output_dir, 'paciente.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono','tipo_seguro','fecha_registro'
        ])
        for i in range(N):
            dni = generate_dni()
            while dni in pacientes_dni:  # Evitar duplicados
                dni = generate_dni()
            pacientes_dni.append(dni)
            
            dob = random_date(
                datetime(1940,1,1).date(),
                datetime(2005,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone,
                random.choice(['SIS','Essalud','Privado','Ninguno']),
                random_date(
                    datetime(2020,1,1).date(),
                    datetime(2025,6,28).date()
                )
            ])

    # 2) Especialidad
    with open(os.path.join(output_dir, 'especialidad.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['nombre','descripcion'])
        for i in range(int(N/100)):
            nombre = f"Especialidad_{i+1}"
            especialidades.append(nombre)
            w.writerow([
                nombre,
                fake.sentence(nb_words=6)
            ])

    # 3) Medico
    with open(os.path.join(output_dir, 'medico.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono'
        ])
        for i in range(int(N/10)):
            dni = generate_dni()
            while dni in medicos_dni or dni in pacientes_dni:  # Evitar duplicados
                dni = generate_dni()
            medicos_dni.append(dni)
            
            dob = random_date(
                datetime(1960,1,1).date(),
                datetime(1990,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone
            ])

    # 4) Medico_Especialidad (Relación N:M)
    with open(os.path.join(output_dir, 'medico_especialidad.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['dni_medico','nombre_especialidad'])
        for i in range(int(N/10)):
            w.writerow([
                random.choice(medicos_dni),
                random.choice(especialidades)
            ])

    # 5) Cabina
    with open(os.path.join(output_dir, 'cabina.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['numero','ubicacion'])
        for i in range(int(N/100)):
            numero = f"C{i+1:04d}"
            cabinas.append(numero)
            w.writerow([
                numero,
                fake.city()
            ])

    # 6) Consultorio
    with open(os.path.join(output_dir, 'consultorio.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['numero','ubicacion'])
        for i in range(int(N/50)):
            numero = f"CONS{i+1:04d}"
            consultorios.append(numero)
            w.writerow([
                numero,
                fake.address()
            ])

    # 7) Personal
    with open(os.path.join(output_dir, 'personal.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono'
        ])
        for i in range(int(N/20)):
            dni = generate_dni()
            while dni in personal_dni or dni in pacientes_dni or dni in medicos_dni:  # Evitar duplicados
                dni = generate_dni()
            personal_dni.append(dni)
            
            dob = random_date(
                datetime(1970,1,1).date(),
                datetime(2000,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone
            ])

    # 8) Turno - Generar todos los días del período con todos los turnos y cabinas
    with open(os.path.join(output_dir, 'turno.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_turno','dni_personal','numero_cabina','fecha','turno'])
        
        # Definir el período completo
        fecha_inicio = datetime(2025, 6, 1).date()
        fecha_fin = datetime(2025, 7, 4).date()
        horarios = ['mañana', 'tarde', 'noche']
        
        # Contador para el ID de turno
        turno_counter = 1
        
        # Iterar por cada día del período
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # Para cada día, generar turnos para cada horario
            for horario in horarios:
                # Para cada horario, generar un turno para cada cabina
                for cabina in cabinas:
                    w.writerow([
                        f"TURNO{turno_counter:08d}",  # ID único con 8 dígitos
                        random.choice(personal_dni),   # Personal asignado aleatoriamente
                        cabina,                        # Cabina específica
                        current_date,                  # Fecha actual
                        horario                        # Horario específico
                    ])
                    turno_counter += 1
            
            # Avanzar al siguiente día
            current_date += timedelta(days=1)
    
    print(f"Generados {turno_counter - 1} turnos cubriendo el período completo 2024-2025")

    # 9) Cita
    with open(os.path.join(output_dir, 'cita.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni_paciente','dni_medico','fecha','hora',
            'estado','dni_personal','numero_consultorio'
        ])
        for i in range(N):
            w.writerow([
                random.choice(pacientes_dni),
                random.choice(medicos_dni),
                random_date(
                    datetime(2024,1,1).date(),
                    datetime(2025,6,28).date()
                ),
                random_time(),
                random.choice(['pendiente','confirmada','cancelada','atendida']),
                random.choice(personal_dni),
                random.choice(consultorios)
            ])

    print(f"Archivos CSV generados con {N} filas cada uno en el directorio: {output_dir}/")

if __name__ == '__main__':
    main()