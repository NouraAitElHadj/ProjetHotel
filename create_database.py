import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Hotel (
        Id_Hotel INTEGER PRIMARY KEY AUTOINCREMENT,
        Ville TEXT NOT NULL,
        Pays TEXT NOT NULL,
        Code_postal INTEGER NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Client (
        Id_Client INTEGER PRIMARY KEY AUTOINCREMENT,
        Adresse TEXT NOT NULL,
        Ville TEXT NOT NULL,
        Code_postal INTEGER NOT NULL,
        Email TEXT NOT NULL,
        Telephone TEXT NOT NULL,
        Nom_complet TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Type_Chambre (
        Id_Type INTEGER PRIMARY KEY AUTOINCREMENT,
        Type TEXT NOT NULL,
        Tarif REAL NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Chambre (
        Id_Chambre INTEGER PRIMARY KEY AUTOINCREMENT,
        Numero INTEGER NOT NULL,
        Etage INTEGER NOT NULL,
        Fumeurs INTEGER NOT NULL,
        Id_Hotel INTEGER NOT NULL,
        Id_Type INTEGER NOT NULL,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
        FOREIGN KEY (Id_Type) REFERENCES Type_Chambre(Id_Type)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Prestation (
        Id_Prestation INTEGER PRIMARY KEY AUTOINCREMENT,
        Prix REAL NOT NULL,
        Description TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation (
        Id_Reservation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_arrivee TEXT NOT NULL,
        Date_depart TEXT NOT NULL,
        Id_Client INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Evaluation (
        Id_Evaluation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        Note INTEGER NOT NULL,
        Commentaire TEXT,
        Id_Client INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Offre (
        Id_Hotel INTEGER NOT NULL,
        Id_Prestation INTEGER NOT NULL,
        PRIMARY KEY (Id_Hotel, Id_Prestation),
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
        FOREIGN KEY (Id_Prestation) REFERENCES Prestation(Id_Prestation)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Contient (
        Id_Reservation INTEGER NOT NULL,
        Id_Chambre INTEGER NOT NULL,
        PRIMARY KEY (Id_Reservation, Id_Chambre),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation),
        FOREIGN KEY (Id_Chambre) REFERENCES Chambre(Id_Chambre)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Fournir (
        Id_Reservation INTEGER NOT NULL,
        Id_Prestation INTEGER NOT NULL,
        PRIMARY KEY (Id_Reservation, Id_Prestation),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation),
        FOREIGN KEY (Id_Prestation) REFERENCES Prestation(Id_Prestation)
    )''')
    
    # Insertion des données initiales
    insert_initial_data(cursor)
    
    conn.commit()
    conn.close()

def insert_initial_data(cursor):
    # Insertion des hôtels
    cursor.executemany('INSERT INTO Hotel (Id_Hotel, Ville, Pays, Code_postal) VALUES (?, ?, ?, ?)', [
        (1, 'Paris', 'France', 75001),
        (2, 'Lyon', 'France', 69002)
    ])
    
    # Insertion des clients
    cursor.executemany('''
    INSERT INTO Client (Id_Client, Adresse, Ville, Code_postal, Email, Telephone, Nom_complet) 
    VALUES (?, ?, ?, ?, ?, ?, ?)''', [
        (1, '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678', 'Jean Dupont'),
        (2, '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789', 'Marie Leroy'),
        (3, '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890', 'Paul Moreau'),
        (4, '27 Rue Nationale', 'Lille', 59800, 'lucie.martin@email.fr', '0645678901', 'Lucie Martin'),
        (5, '3 Rue des Fleurs', 'Nice', 6000, 'emma.giraud@email.fr', '0656789012', 'Emma Giraud')
    ])
    
    # Insertion des prestations
    cursor.executemany('INSERT INTO Prestation (Id_Prestation, Prix, Description) VALUES (?, ?, ?)', [
        (1, 15, 'Petit-déjeuner'),
        (2, 30, 'Navette aéroport'),
        (3, 0, 'Wi-Fi gratuit'),
        (4, 50, 'Spa et bien-être'),
        (5, 20, 'Parking sécurisé')
    ])
    
    # Insertion des types de chambre
    cursor.executemany('INSERT INTO Type_Chambre (Id_Type, Type, Tarif) VALUES (?, ?, ?)', [
        (1, 'Simple', 80),
        (2, 'Double', 120)
    ])
    
    # Insertion des chambres
    cursor.executemany('''
    INSERT INTO Chambre (Id_Chambre, Numero, Etage, Fumeurs, Id_Hotel, Id_Type) 
    VALUES (?, ?, ?, ?, ?, ?)''', [
        (1, 201, 2, 0, 1, 1),
        (2, 502, 5, 1, 1, 2),
        (3, 305, 3, 0, 2, 1),
        (4, 410, 4, 0, 2, 2),
        (5, 104, 1, 1, 2, 2),
        (6, 202, 2, 0, 1, 1),
        (7, 307, 3, 1, 1, 2),
        (8, 101, 1, 0, 1, 1)
    ])
    
    # Insertion des réservations
    cursor.executemany('''
    INSERT INTO Reservation (Id_Reservation, Date_arrivee, Date_depart, Id_Client) 
    VALUES (?, ?, ?, ?)''', [
        (1, '2025-06-15', '2025-06-18', 1),
        (2, '2025-07-01', '2025-07-05', 2),
        (3, '2025-08-10', '2025-08-14', 3),
        (4, '2025-09-05', '2025-09-07', 4),
        (5, '2025-09-20', '2025-09-25', 5),
        (7, '2025-11-12', '2025-11-14', 2),
        (9, '2026-01-15', '2026-01-18', 4),
        (10, '2026-02-01', '2026-02-05', 2)
    ])
    
    # Insertion des évaluations
    cursor.executemany('''
    INSERT INTO Evaluation (Id_Evaluation, Date, Note, Commentaire, Id_Client) 
    VALUES (?, ?, ?, ?, ?)''', [
        (1, '2025-06-15', 5, 'Excellent séjour, personnel très accueillant.', 1),
        (2, '2025-07-01', 4, 'Chambre propre, bon rapport qualité/prix.', 2),
        (3, '2025-08-10', 3, 'Séjour correct mais bruyant la nuit.', 3),
        (4, '2025-09-05', 5, 'Service impeccable, je recommande.', 4),
        (5, '2025-09-20', 4, 'Très bon petit-déjeuner, hôtel bien situé.', 5)
    ])
    
    # Insertion des relations Contient
    cursor.executemany('INSERT INTO Contient (Id_Reservation, Id_Chambre) VALUES (?, ?)', [
        (1, 1), (2, 3), (3, 4), (4, 5), (5, 2), (7, 7), (9, 6), (10, 8)
    ])
    
    # Insertion des relations Offre
    cursor.executemany('INSERT INTO Offre (Id_Hotel, Id_Prestation) VALUES (?, ?)', [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
        (2, 1), (2, 3), (2, 5)
    ])
    
    # Insertion des relations Fournir
    cursor.executemany('INSERT INTO Fournir (Id_Reservation, Id_Prestation) VALUES (?, ?)', [
        (1, 1), (1, 3),
        (2, 3),
        (3, 1), (3, 5),
        (4, 1),
        (5, 1), (5, 4),
        (7, 3),
        (9, 1),
        (10, 1), (10, 3)
    ])

if __name__ == '__main__':
    create_database()