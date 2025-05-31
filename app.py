import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connexion à la base de données
conn = sqlite3.connect('hotel.db')

# Fonctions utilitaires
def get_reservations():
    query = '''
    SELECT r.Id_Reservation, r.Date_arrivee, r.Date_depart, c.Nom_complet, h.Ville, ch.Numero, ch.Etage
    FROM Reservation r
    JOIN Client c ON r.Id_Client = c.Id_Client
    JOIN Contient co ON r.Id_Reservation = co.Id_Reservation
    JOIN Chambre ch ON co.Id_Chambre = ch.Id_Chambre
    JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
    '''
    return pd.read_sql(query, conn)

def get_clients():
    return pd.read_sql('SELECT * FROM Client', conn)

def get_available_rooms(start_date, end_date):
    query = '''
    SELECT ch.Id_Chambre, ch.Numero, ch.Etage, t.Type, t.Tarif, h.Ville
    FROM Chambre ch
    JOIN Type_Chambre t ON ch.Id_Type = t.Id_Type
    JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
    WHERE ch.Id_Chambre NOT IN (
        SELECT co.Id_Chambre
        FROM Contient co
        JOIN Reservation r ON co.Id_Reservation = r.Id_Reservation
        WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
    )
    '''
    return pd.read_sql(query, conn, params=(end_date, start_date))

def add_client(adresse, ville, code_postal, email, telephone, nom_complet):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Client (Adresse, Ville, Code_postal, Email, Telephone, Nom_complet)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (adresse, ville, code_postal, email, telephone, nom_complet))
    conn.commit()
    st.success('Client ajouté avec succès!')

def add_reservation(id_client, id_chambre, date_arrivee, date_depart):
    cursor = conn.cursor()
    try:
        # Vérifier si la chambre est disponible
        cursor.execute('''
        SELECT COUNT(*) FROM Contient co
        JOIN Reservation r ON co.Id_Reservation = r.Id_Reservation
        WHERE co.Id_Chambre = ? AND (r.Date_arrivee <= ? AND r.Date_depart >= ?)
        ''', (id_chambre, date_depart, date_arrivee))
        
        if cursor.fetchone()[0] > 0:
            st.error('La chambre n\'est pas disponible pour ces dates.')
            return
        
        # Ajouter la réservation
        cursor.execute('''
        INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client)
        VALUES (?, ?, ?)
        ''', (date_arrivee, date_depart, id_client))
        
        # Récupérer l'ID de la nouvelle réservation
        id_reservation = cursor.lastrowid
        
        # Lier la chambre à la réservation
        cursor.execute('''
        INSERT INTO Contient (Id_Reservation, Id_Chambre)
        VALUES (?, ?)
        ''', (id_reservation, id_chambre))
        
        conn.commit()
        st.success('Réservation ajoutée avec succès!')
    except Exception as e:
        conn.rollback()
        st.error(f'Erreur lors de l\'ajout de la réservation: {e}')

# Interface Streamlit
st.title('Système de Gestion Hôtelière')

menu = st.sidebar.selectbox('Menu', [
    'Consulter les réservations',
    'Consulter les clients',
    'Chambres disponibles',
    'Ajouter un client',
    'Ajouter une réservation'
])

if menu == 'Consulter les réservations':
    st.header('Liste des réservations')
    reservations = get_reservations()
    st.dataframe(reservations)

elif menu == 'Consulter les clients':
    st.header('Liste des clients')
    clients = get_clients()
    st.dataframe(clients)

elif menu == 'Chambres disponibles':
    st.header('Recherche de chambres disponibles')
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Date d\'arrivée', datetime.now())
    with col2:
        end_date = st.date_input('Date de départ', datetime.now())
    
    if start_date >= end_date:
        st.error('La date de départ doit être après la date d\'arrivée.')
    else:
        rooms = get_available_rooms(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if len(rooms) > 0:
            st.dataframe(rooms)
        else:
            st.warning('Aucune chambre disponible pour ces dates.')

elif menu == 'Ajouter un client':
    st.header('Ajouter un nouveau client')
    
    with st.form('client_form'):
        nom_complet = st.text_input('Nom complet')
        adresse = st.text_input('Adresse')
        ville = st.text_input('Ville')
        code_postal = st.number_input('Code postal', min_value=0, step=1)
        email = st.text_input('Email')
        telephone = st.text_input('Téléphone')
        
        submitted = st.form_submit_button('Ajouter')
        if submitted:
            if nom_complet and adresse and ville and email and telephone:
                add_client(adresse, ville, code_postal, email, telephone, nom_complet)
            else:
                st.error('Veuillez remplir tous les champs obligatoires.')

elif menu == 'Ajouter une réservation':
    st.header('Ajouter une nouvelle réservation')
    
    # Récupérer la liste des clients
    clients = get_clients()
    client_options = {row['Id_Client']: f"{row['Nom_complet']} ({row['Ville']})" for _, row in clients.iterrows()}
    
    with st.form('reservation_form'):
        # Sélection du client
        selected_client = st.selectbox(
            'Client',
            options=list(client_options.keys()),
            format_func=lambda x: client_options[x]
        )
        
        # Dates de séjour
        col1, col2 = st.columns(2)
        with col1:
            date_arrivee = st.date_input('Date d\'arrivée', datetime.now())
        with col2:
            date_depart = st.date_input('Date de départ', datetime.now())
        
        # Recherche des chambres disponibles
        if date_arrivee >= date_depart:
            st.error('La date de départ doit être après la date d\'arrivée.')
        else:
            rooms = get_available_rooms(date_arrivee.strftime('%Y-%m-%d'), date_depart.strftime('%Y-%m-%d'))
            
            if len(rooms) > 0:
                # Formatage des options de chambre
                room_options = {
                    row['Id_Chambre']: f"Chambre {row['Numero']} (Étage {row['Etage']}, {row['Type']}, {row['Tarif']}€, {row['Ville']})"
                    for _, row in rooms.iterrows()
                }
                
                selected_room = st.selectbox(
                    'Chambre disponible',
                    options=list(room_options.keys()),
                    format_func=lambda x: room_options[x]
                )
                
                submitted = st.form_submit_button('Réserver')
                if submitted:
                    add_reservation(
                        selected_client,
                        selected_room,
                        date_arrivee.strftime('%Y-%m-%d'),
                        date_depart.strftime('%Y-%m-%d')
                    )
            else:
                st.warning('Aucune chambre disponible pour ces dates.')

# Fermer la connexion à la base de données
conn.close()