from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Satellite_New, Satellite_Master, Master_Edit_Record, User, Satellite_Removed, ApproveDenyTable, ScrapeRecord, New_Edit_Record, Satellite_Duplicates, Master_Pending, Master_Manual_Record
from functools import wraps
import os
import traceback
import jwt
from sqlalchemy import func
from datetime import datetime, timedelta
import subprocess
from sqlalchemy import not_


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/removed', methods=['GET'])
def get_removed_satellites():
    try:
        # Query the skynet_satellites table for removed satellites (data_status = 1)
        results = db.session.query(
            Satellite_Master, 
            Master_Pending.reason
        ).join(
            Master_Pending, 
            Satellite_Master.cospar == Master_Pending.cospar
        ).filter(Satellite_Master.data_status == 3).all()

        # Serialize the results into a list of dictionaries
        data = [
            {
                **row.Satellite_Master.to_dict(), 
                "removal_reason": row.reason
            } for row in results
        ]

        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Debugging: Check values
        print("Debug - Username: ", user.username)
        print("Debug - Login Date: ", datetime.now().date().isoformat())
        print("Debug - Secret Key: ", app.config['SECRET_KEY'])

        # Generate token
        token = jwt.encode({
            'username': user.username,
            'login_date': datetime.now().date().isoformat(),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        # Debugging: Check token
        print("Debug - Generated Token: ", token)

        return jsonify({'token': token, 'username': user.username}), 200

    return jsonify({'error': 'Invalid username or password'}), 401


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        # Debugging: Check received token
        print("Debug - Received Token: ", token)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Debugging: Check decoded data
            print("Debug - Decoded Data: ", data)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/some-protected-route')
@token_required
def protected_route():
    return 'This is a protected route.'

@app.route('/api/satellites_duplicate', methods=['GET'])
def get_satellites_duplicate():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit

        # Search query parameter
        search_query = request.args.get('search', '', type=str)

        # Query with optional filtering
        query = Satellite_Duplicates.query
        if search_query:
            query = query.filter(func.lower(Satellite_Duplicates.cospar).like(f'%{search_query.lower()}%'))  # Example for filtering by name

        # Get total count after filtering
        total_count = query.count()

        # Apply pagination
        results = query.offset(offset).limit(limit).all()

        # Convert data to dict
        data = [row.to_dict() for row in results]

        return jsonify({
            'data': data,
            'total_count': total_count
        })

    except Exception as e:
        error_details = traceback.format_exc()
        print("Error:", error_details)  # Now printing the full stack trace
        return jsonify({'error': str(error_details)}), 500
    
#NEW_LAUNCHES
@app.route('/api/satellites_new', methods=['GET'])
def get_satellites_new():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit

        # Search query parameter
        search_query = request.args.get('search', '', type=str)

        # Data status filter parameter
        data_status_filter = request.args.get('data_status')

        # Query with optional filtering
        query = Satellite_New.query

        # Apply search query filter if provided
        if search_query:
            query = query.filter(func.lower(Satellite_New.cospar).like(f'%{search_query.lower()}%'))

        # Apply data status filter if provided
        if data_status_filter:
            query = query.filter(Satellite_New.data_status == data_status_filter)

        # Get total count after filtering
        total_count = query.count()

        # Apply pagination
        results = query.offset(offset).limit(limit).all()

        # Convert data to dict
        data = [row.to_dict() for row in results]

        return jsonify({
            'data': data,
            'total_count': total_count
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500
    
#master_dataset
@app.route('/api/satellites_master', methods=['GET'])
def get_satellites_master():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit

        # Search query parameter
        search_query = request.args.get('search', '', type=str)

        # Data status filter parameter
        data_status_filter = request.args.get('data_status')

        # Query with optional filtering
        query = Satellite_Master.query.filter(not_(Satellite_Master.data_status.in_([3])))

        # Apply search query filter if provided
        if search_query:
            query = query.filter(func.lower(Satellite_Master.cospar).like(f'%{search_query.lower()}%'))

        # Apply data status filter if provided
        if data_status_filter:
            query = query.filter(Satellite_Master.data_status == data_status_filter)

        # Get total count after filtering
        total_count = query.count()

        # Apply pagination
        results = query.offset(offset).limit(limit).all()

        # Convert data to dict
        data = [row.to_dict() for row in results]

        return jsonify({
            'data': data,
            'total_count': total_count
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

#NEW_LAUNCHES
@app.route('/api/satellites_removed', methods=['GET'])
def get_satellites_removed():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit

        # Search query parameter
        search_query = request.args.get('search', '', type=str)

        query = Satellite_Removed.query
        if search_query:
            query = query.filter(func.lower(Satellite_Removed.cospar).like(f'%{search_query.lower()}%'))  # Example for filtering by name

        # Get total count after filtering
        total_count = query.count()

        # Apply pagination
        results = query.offset(offset).limit(limit).all()

        # Convert data to dict
        data = [row.to_dict() for row in results]

        return jsonify({
            'data': data,
            'total_count': total_count
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500





@app.route('/api/master_satellites_remove', methods=['POST'])
def master_satellites_remove():
    data = request.get_json()
    updates = data['updates']
    name = data.get('name', 'Unknown')
    current_date = datetime.utcnow()  # Use UTC time for consistency

    try:
        for update in updates:
            cospar = update['cospar']
            reason = update['reason']

            # Fetch the old data_status from Master_Pending
            pending_record = Master_Pending.query.filter_by(cospar=cospar).first()
            old_data_status = pending_record.old_data_status if pending_record else None

            # Fetch the satellite to be removed
            satellite = Satellite_Master.query.filter_by(cospar=cospar).first()
            if satellite:
                if old_data_status is not None:
                    satellite.data_status = old_data_status  # Set to old data_status

                # Prepare data for Satellite_Removed
                removed_data = satellite.to_dict()  # Convert to dict and remove 'id'
                removed_data.pop('id', None)  # Remove the 'id' key
                removed_satellite = Satellite_Removed(
                    **removed_data,
                    username=name,
                    removal_source='ucs_master',
                    removal_reason=reason
                )
                db.session.add(removed_satellite)
                # Delete the entry from Satellite_Master
                db.session.delete(satellite)
                print(f"Deleted entry from Satellite_Master for {cospar} and added to Satellite_Removed")

        db.session.commit()
        return jsonify({"message": "Satellite removed from Satellite_Master and added to Satellite_Removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # Debug print
        return jsonify({"error": str(e)}), 500
    







@app.route('/api/edit-data', methods=['POST'])
def master_edit_data():
    try:
        data = request.json
        edit_records = data['edit_records']
        edited_by = data['name']

        print("Received edit records:", edit_records)  # Debug print

        for record in edit_records:
            print(f"Processing record for cospar: {record['cospar']}")  # Debug print

            # Insert into satellite_edit_records
            new_edit_record = Master_Edit_Record(
                cospar=record['cospar'],
                column_name=record['column'],
                old_value=record['oldValue'],
                new_value=record['newValue'],
                edited_by=edited_by
            )
            db.session.add(new_edit_record)

            # Update skynet_satellites
            update_result = Satellite_Master.query.filter_by(cospar=record['cospar']).update(
                {record['column']: record['newValue']})
            print(f"Update result for satellite_name {record['cospar']}: {update_result}")  # Debug print

        db.session.commit()
        return jsonify({'message': 'Data updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # More detailed error message
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-edit-records', methods=['GET'])
def get_master_edit_records():
    try:
        
        # Log at the start
        app.logger.info('get_edit_records function called')

        # Query all records in the satellite_edit_records table
        records = Master_Edit_Record.query.all()

        # Log query execution
        app.logger.info(f'Query executed, retrieved {len(records)} records')

        # Serialize the records into a list of dictionaries
        data = [record.to_dict() for record in records]

        # Log before returning
        app.logger.info('Successfully serialized the records')

        return jsonify(data), 200
    except Exception as e:
        # Log the full exception
        app.logger.error('Error in get_edit_records: ' + str(e))
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-manual-records', methods=['GET'])
def get_manual_records():
    try:
        
        # Log at the start
        app.logger.info('get_edit_records function called')

        # Query all records in the satellite_edit_records table
        records = Master_Manual_Record.query.all()

        # Log query execution
        app.logger.info(f'Query executed, retrieved {len(records)} records')

        # Serialize the records into a list of dictionaries
        data = [record.to_dict() for record in records]

        # Log before returning
        app.logger.info('Successfully serialized the records')

        return jsonify(data), 200
    except Exception as e:
        # Log the full exception
        app.logger.error('Error in get_edit_records: ' + str(e))
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/ucs_new/edit-data', methods=['POST'])
def new_edit_data():
    try:
        data = request.json
        edit_records = data['edit_records']
        edited_by = data['name']

        print("Received edit records:", edit_records)  # Debug print

        for record in edit_records:
            print(f"Processing record for cospar: {record['cospar']}")  # Debug print

            # Insert into satellite_edit_records
            new_edit_record = New_Edit_Record(
                cospar=record['cospar'],
                column_name=record['column'],
                old_value=record['oldValue'],
                new_value=record['newValue'],
                edited_by=edited_by
            )
            db.session.add(new_edit_record)

            # Update skynet_satellites
            update_result = Satellite_New.query.filter_by(cospar=record['cospar']).update(
                {record['column']: record['newValue']})
            print(f"Update result for satellite_name {record['cospar']}: {update_result}")  # Debug print

        db.session.commit()
        return jsonify({'message': 'Data updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # More detailed error message
        return jsonify({'error': str(e)}), 500


@app.route('/api/ucs_duplicate/edit-data', methods=['POST'])
def duplicate_edit_data():
    try:
        data = request.json
        edit_records = data['edit_records']
        edited_by = data['name']

        print("Received edit records:", edit_records)  # Debug print

        for record in edit_records:
            record_id = record['id']  # Assuming 'id' is sent in each edit record
            print(f"Processing record for ID: {record_id}")  # Debug print

            # Update Satellite_Duplicates based on id
            update_result = Satellite_Duplicates.query.filter_by(id=record_id).update(
                {record['column']: record['newValue']})
            print(f"Update result for ID {record_id}: {update_result}")  # Debug print

        db.session.commit()
        return jsonify({'message': 'Data updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # More detailed error message
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/ucs_new/get-edit-records', methods=['GET'])
def get_new_edit_records():
    try:
        
        # Log at the start
        app.logger.info('get_edit_records function called')

        # Query all records in the satellite_edit_records table
        records = New_Edit_Record.query.all()

        # Log query execution
        app.logger.info(f'Query executed, retrieved {len(records)} records')

        # Serialize the records into a list of dictionaries
        data = [record.to_dict() for record in records]

        # Log before returning
        app.logger.info('Successfully serialized the records')

        return jsonify(data), 200
    except Exception as e:
        # Log the full exception
        app.logger.error('Error in get_edit_records: ' + str(e))
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/remove-sat', methods=['POST'])
def remove_sat():
    data = request.get_json()
    cospar_id = data.get('cospar')
    reason = data.get('reason')
    old_data_status = data.get('old_data_status')

    try:
        # Find the satellite using the cospar ID
        satellite = Satellite_Master.query.filter_by(cospar=cospar_id).first()
        if not satellite:
            return jsonify({'error': 'Satellite not found'}), 404

        # Update the satellite status to indicate it has been removed
        satellite.data_status = 3
        db.session.add(satellite)

        # Create a new removal record
        new_removal_record = Master_Pending(old_data_status = old_data_status, cospar=cospar_id, reason=reason)
        db.session.add(new_removal_record)

        db.session.commit()
        return jsonify({'message': 'Satellite removed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    try:
        data = request.get_json()
        username = data['name']
        # Existing code
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Adjusting to get the desired path
        desired_path = os.path.dirname(os.path.dirname(base_dir))

        script_path = os.path.join(desired_path, 'CS639Skynet', 'skynet_scrapy', 'myspider', 'skynet.py')
        print(script_path)

        # Run the command
        subprocess.run(['python', script_path], check=True)
        scraper_completion(username)
        return jsonify({"message": "Scraper started successfully"}), 200
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the scraper: {e}")
        return jsonify({'error': 'Failed to run scraper'}), 500
    except Exception as e:
        print(f"General Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/scraper-completion', methods=['POST'])
def scraper_completion(username):
    try:

        # Create a new ScrapeRecord instance
        new_record = ScrapeRecord(username=username)
        db.session.add(new_record)
        db.session.commit()

        return jsonify({'message': 'New scrape record added successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/scrape-records', methods=['GET'])
def get_scrape_records():
    try:
        print("Fetching scrape records...")
        records = ScrapeRecord.query.all()

        print(f"Records fetched: {records}")

        # Convert the records to a list of dictionaries
        data = [record.to_dict() for record in records]

        print(f"Data to return: {data}")

        return jsonify(data), 200
    except Exception as e:
        print(f"Error fetching scrape records: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ucs_new/new_satellites_approve', methods=['POST'])
def new_confirm_approval():
    print('Function confirm_approval called')

    data = request.get_json()
    row_data = data.get('row')  # This will be a dictionary containing the row data
    print(row_data)
    
    name = data.get('name', 'Unknown')
    reason = data.get('reason')
    print(f'Received name: {name}')

    current_date = datetime.now()
    print(f'Current date: {current_date}')

    try:
        # Remove 'editing' key from row_data if it exists
        row_data.pop('editing', None)

                # Update the data_status in Satellites_New
        satellite_new = Satellite_New.query.filter_by(cospar=row_data.get('cospar')).first()
        if satellite_new:
            db.session.delete(satellite_new)
            print(f"Updated data_status in Satellites_New for {row_data.get('cospar')}")

        # Create a new instance for Satellite_Master using the row data
        new_satellite = Satellite_Master(**row_data)
        db.session.add(new_satellite)
        print(f"New satellite added to Satellite_Master: {row_data}")

        # Insert a record into ApproveDenyTable
        approval_record = ApproveDenyTable(name=name, date=current_date, cospar=row_data.get('cospar'), action="approve", reason = reason)
        db.session.add(approval_record)
        print(f"Added record to ApproveDenyTable for satellite {row_data.get('cospar')}")

        db.session.commit()
        return jsonify({"message": "New satellite added to Satellite_Master and approval record added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f'Exception occurred: {e}')  # Debug print
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ucs_new/duplicate_satellites_approve', methods=['POST'])
def duplicate_confirm_approval():
    try:
        data = request.get_json()
        duplicate_id = data.get('id') 
        row_data = data.get('row')
        name = data.get('name', 'Unknown')

        print(f'Received data: {data}')

        # Remove 'editing' and 'id' keys from row_data
        row_data.pop('editing', None)
        row_data.pop('id', None)

        satellite_duplicate = Satellite_Duplicates.query.get(duplicate_id)
        if satellite_duplicate:
            new_satellite = Satellite_Master(**row_data)
            db.session.add(new_satellite)
            db.session.delete(satellite_duplicate)
            db.session.commit()

            return jsonify({"message": "New satellite added to Satellite_Master"}), 200
        else:
            return jsonify({"error": "Satellite duplicate not found"}), 404
    except Exception as e:
        db.session.rollback()
        print(f'Exception occurred: {e}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/ucs_new/new_satellites_deny', methods=['POST'])
def new_deny_approval():
    print('Function deny_approval called')

    data = request.get_json()
    row_data = data.get('row')
    name = data.get('name', 'Unknown')
    reason = data.get('reason')
    cospar = row_data.get('cospar')

    try:
        # Find the satellite entry in Satellite_New by cospar
        satellite_new = Satellite_New.query.filter_by(cospar=cospar).first()
        if satellite_new:
            # Add to Satellite_Removed
            removed_satellite = Satellite_Removed(
                **satellite_new.to_dict(), 
                username=name,# Convert to dict and remove 'id'
                removal_source='ucs_new',
                removal_reason=reason
            ) 
            db.session.add(removed_satellite)
            db.session.delete(satellite_new)

            # Insert a record into ApproveDenyTable
            denial_record = ApproveDenyTable(name=name, date=datetime.now(), cospar=cospar, action="deny", reason=reason)
            db.session.add(denial_record)
            print(f"Added denial record to ApproveDenyTable for satellite {cospar}")

            # Delete the entry from Satellite_New
            db.session.delete(satellite_new)
            print(f"Deleted entry from Satellite_New for {cospar}")

        db.session.commit()
        return jsonify({"message": "Satellite denial confirmed, record added to Removed and deleted from New"}), 200
    except Exception as e:
        db.session.rollback()
        print(f'Exception occurred: {e}')  # Debug print
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ucs_new/duplicate_satellites_deny', methods=['POST'])
def duplicates_deny_approval():
    print('Function deny_approval called')

    data = request.get_json()
    row_data = data.get('row')  # This will be a dictionary containing the row data
    name = data.get('name', 'Unknown')
    reason = data.get('reason')
    
    duplicate_id = row_data.get('id')  # Use the primary key 'id' for deletion

    try:
        # Find the satellite entry in Satellite_Duplicates by ID
        satellite_duplicate = Satellite_Duplicates.query.get(duplicate_id)
        if satellite_duplicate:
            # Add to Satellite_Removed
            removed_data = satellite_duplicate.to_dict()  # Convert to dict
            removed_data.pop('id', None)  # Remove the 'id' key
            removed_satellite = Satellite_Removed(
                **removed_data,
                removal_source='ucs_duplicate',
                username=name,
                removal_reason=reason
            )
            db.session.add(removed_satellite)

            # Delete the entry from Satellite_Duplicates
            db.session.delete(satellite_duplicate)
            print(f"Deleted entry from Satellite_Duplicates with ID {duplicate_id}")

        db.session.commit()
        return jsonify({"message": "Satellite denial confirmed, record added to Removed and deleted from Duplicates"}), 200
    except Exception as e:
        db.session.rollback()
        print(f'Exception occurred: {e}')  # Debug print
        return jsonify({"error": str(e)}), 500

@app.route('/api/new_history', methods=['GET'])
def get_new_history():
    try:
        # Perform the query to get all records from ApproveDenyTable
        results = ApproveDenyTable.query.all()

        # Serialize the results into a list of dictionaries
        data = [{'name': r.name, 'date': r.date, 'cospar': r.cospar, 'action': r.action, 'reason':r.reason} for r in results]

        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ucs_new/history/details', methods=['GET'])
def get_new_removed_sat_details():
    try:
        cospar = request.args.get('cospar')

        # Perform a join with the SatelliteRemovalRecord table
        results = db.session.query(
            Satellite_New, 
            ApproveDenyTable.reason
        ).outerjoin(
            ApproveDenyTable, 
            Satellite_New.cospar == ApproveDenyTable.cospar
        ).filter(Satellite_New.cospar == cospar).all()

        # Serialize the results
        satellites_details = []
        for satellite, reason in results:
            satellite_dict = satellite.to_dict()
            satellite_dict['removal_reason'] = reason
            satellites_details.append(satellite_dict)

        return jsonify(satellites_details)
    except Exception as e:
        app.logger.error('Error in get_cospar_details: ' + str(e))
        return jsonify({"error": str(e)}), 500



@app.route('/api/manual-add-stat', methods=['POST'])
def manual_add_stat():
    try:
        # Extract data from request
        data = request.json
        instance = data


        # Create a record for manual addition in Master_Manual_Record
        new_manual_record = Master_Manual_Record(
            cospar=instance.get('cospar'),
            edited_by=data.get('username')  # Assuming 'username' is passed in the request
        )
        db.session.add(new_manual_record)

        print("Received new data for addition:", instance)  # Debug print

        # Create a new Satellite_Master instance
        new_satellite = Satellite_Master(
            # Assuming you have columns like 'cospar', 'name', 'official_name', etc.
            full_name = instance.get('full_name'),
            official_name = instance.get('official_name'),
            country = instance.get('country'),
            owner_country = instance.get('owner_country'),
            owner = instance.get('owner'),
            users = instance.get('users'),
            purpose = instance.get('purpose'),
            detail_purpose = instance.get('detail_purpose'),
            orbit_class = instance.get('orbit_class'),
            orbit_type = instance.get('orbit_type'),
            in_geo = instance.get('in_geo'),
            perigee = instance.get('perigee'),
            apogee = instance.get('apogee'),
            eccentricity = instance.get('eccentricity'),
            inclination = instance.get('inclination'),
            period = instance.get('period'),
            mass = instance.get('mass'),
            dry_mass = instance.get('dry_mass'),
            power = instance.get('power'),
            launch_date = instance.get('launch_date'),
            expected_lifetime = instance.get('expected_lifetime'),
            contractor = instance.get('contractor'),
            contractor_country = instance.get('contractor_country'),
            launch_site = instance.get('launch_site'),
            launch_vehicle = instance.get('launch_vehicle'),
            cospar = instance.get('cospar'),
            norad = instance.get('norad'),
            data_status =  instance.get('data_status'),
            source = instance.get('source'),
            additional_source = instance.get('additional_source'),
        )

        # Add the new instance to the database
        db.session.add(new_satellite)
        db.session.commit()

        return jsonify({'message': 'New satellite added successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # More detailed error message
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/pending_unremove_satellite', methods=['POST'])
def pending_unremove_satellite():
    data = request.get_json()
    cospar = data.get('cospar')

    try:
        # Find the satellite in Satellite_Master
        satellite = Satellite_Master.query.filter_by(cospar=cospar).first()
        if satellite:
            # Fetch the removal record to determine the rollback status
            removal_record = Master_Pending.query.filter_by(cospar=cospar).first()
            if removal_record:
                # Roll back data_status to previous status
                satellite.data_status = removal_record.old_data_status  # Assuming the previous status is stored

                # Delete the removal record
                db.session.delete(removal_record)
            else:
                # Handle case where no removal record is found
                # Optionally, set a default status or handle the error
                satellite.data_status = 1  # Example default status

            db.session.commit()
            return jsonify({"message": "Satellite un-removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ucs_unremove_satellite', methods=['POST'])
def ucs_unremove_satellite():
    data = request.json
    removed_satellite_id = data.get('id')
    print(f"Received request to unremove satellite with ID: {removed_satellite_id}")

    try:
        # Fetch the removed satellite data using its unique ID
        removed_satellite = db.session.get(Satellite_Removed, removed_satellite_id)
        print(f"Retrieved Removed Satellite: {removed_satellite}")

        if not removed_satellite:
            print(f"Satellite not found in removed records for ID: {removed_satellite_id}")
            return jsonify({"error": "Satellite not found in removed records"}), 404
        
        satellite_data = removed_satellite.to_dict()
        # Remove fields not relevant to the Satellite_Duplicates model
        satellite_data.pop('username', None)
        satellite_data.pop('removal_date', None)
        satellite_data.pop('removal_reason', None)
        satellite_data.pop('removal_source', None)
        satellite_data.pop('id', None)
        # Determine the original source table and create a new instance in that table
        if removed_satellite.removal_source == 'ucs_master':
            new_satellite = Satellite_Master(**satellite_data)
            db.session.add(new_satellite)
            print(f"Adding satellite back to UCS_Master: {new_satellite}")
        elif removed_satellite.removal_source == 'ucs_new':
            new_satellite = Satellite_New(**satellite_data)
            db.session.add(new_satellite)
            print(f"Adding satellite back to UCS_New: {new_satellite}")
        elif removed_satellite.removal_source == 'ucs_duplicate':
            new_satellite = Satellite_Duplicates(**satellite_data)
            db.session.add(new_satellite)
            print(f"Adding satellite back to UCS_Duplicate: {new_satellite}")

        # Delete the record from Satellite_Removed
        db.session.delete(removed_satellite)
        print(f"Deleted satellite from Satellite_Removed: {removed_satellite}")

        db.session.commit()
        print("Database commit successful")
        return jsonify({"message": "Satellite un-removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/alldata', methods=['GET'])
def export_master():
    try:
        # Query all data from the Satellite_Master table
        all_data = Satellite_Master.query.all()

        # Convert data to a list of dictionaries
        data_list = [item.to_dict() for item in all_data]  # Assuming you have a to_dict method

        return jsonify(data_list)

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': 'Failed to fetch data'}), 500

    

if __name__ == "__main__":
    app.run(debug=True, port=8000)
