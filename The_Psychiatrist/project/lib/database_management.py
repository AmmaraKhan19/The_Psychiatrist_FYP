import os, datetime
from sqlalchemy.sql.expression import false
import helper
from sqlalchemy.sql.sqltypes import DateTime, VARCHAR
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin

###########################################
## SCHEMA #################################
###########################################


Base = declarative_base()
engine = create_engine(helper.config["sql_database_uri"], echo=False)
Session = sessionmaker(bind=engine)

class Admin(UserMixin, Base):
    __tablename__ = "admin"
    
    id = Column(Integer,primary_key = True)
    username = Column(String(100), unique = True, nullable=false)
    password = Column(VARCHAR(100), nullable=false)

class User(UserMixin, Base):
    __tablename__ = "user"
    
    id = Column(Integer,primary_key = True)
    first_name = Column(String(1000), nullable=false)
    last_name = Column(String(1000), nullable=false)
    username = Column(String(100), unique = True, nullable=false)
    email = Column(String(100), unique = True, nullable=false)
    password = Column(String(100))
    role = Column(String, nullable=false)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

class Results(Base):
    __tablename__ = "results"

    id = Column(Integer,primary_key = True)
    user_id = Column(Integer, nullable = False)
    tweet_id = Column(Integer, nullable = False)
    tweet_text = Column(String, nullable = False)
    ideation = Column(String, nullable = False)
    status = Column(String, nullable = False)

###########################################
## Database Initiation ####################
###########################################

if not(os.path.exists('./project/db/psychiatrist.db')):
    helper.log("debug","db","Running for the first time as no previous DB found")
    helper.log("debug","db","Creating database")
    Base.metadata.create_all(engine)
    basic_admin = Admin(password=helper.config["password"], username=helper.config["username"])
    session = Session()
    session.add(basic_admin)
    session.commit()
    session.close()
helper.log("critical","db","Database inititated successfully")


###########################################
## Database Functions #####################
###########################################

## Admin login ##########
def admin_login_query(username,password):
    session = Session()
    validation = session.query(Admin).filter_by(username = username).first()
    session.close()
    if validation is None:
        helper.log('critical','db',"no such user")
        return False, 0
    elif validation is not None:
        if validation.username == username and validation.password == password:
            helper.log('critical','db',"correct credentials")
            return True, validation.id
        else:
            helper.log('critical','db',"incorrect credentials")
            return False, 0
    return False, 0

## Save new user into database #################
def write_user_to_db(firstname,lastname,email,username,password):
    session = Session()
    try:
        helper.log("critical","db","trying to write user")
        new_user = User(first_name=firstname,last_name=lastname,email=email,username=username,password=password,role="User")
    except Exception as E:
        print(E)
        helper.log('critical','db',"Session error, unable to add new user")
        return False
    session.add(new_user)
    session.commit()
    session.close()
    return True    

## Save identified case into database ##########
def write_tweet_to_db(predicted_tweet):
    session = Session()
    try:
        helper.log("critical","db","trying to write tweet")
        new_tweet = Results(user_id=predicted_tweet["user_id"], tweet_id=predicted_tweet["tweet_id"], tweet_text=predicted_tweet["tweet_text"], ideation=predicted_tweet["ideation"], status=predicted_tweet["status"])
    except Exception as E:
        print(E)
        helper.log('critical','db',"Session error, unable to add new tweet")
        return False
    session.add(new_tweet)
    session.commit()
    session.close()
    return True

## Read identified case from database ##########
def read_cases():
    session = Session()
    all_cases = session.query(Results.id, Results.user_id, Results.tweet_id, Results.tweet_text, Results.ideation, Results.status).all()
    session.close()
    return all_cases

## User login ##########
def login_query(username,password):
    session = Session()
    validation = session.query(User).filter_by(username = username).first()
    session.close()
    if validation is None:
        helper.log('critical','db',"no such user")
        return False, 0
    elif validation is not None:
        if validation.username == username and validation.password == password:
            helper.log('critical','db',"correct credentials")
            return True, validation.id
        else:
            helper.log('critical','db',"incorrect credentials")
            return False, 0
    return False, 0

##  Read specific case status from database ##########
def case_status(case_id):
    helper.log('critical','db',"trying to get case status")
    session = Session()
    case_to_update = session.query(Results).filter_by(id=case_id).first()
    session.close()
    if case_to_update is None:
        helper.log('critical','db',"no such case")
        return "None"
    elif case_to_update is not None:
        return case_to_update
    return "None"

## Save updated case status into database ##########
def write_status_to_db(case_to_update):
    try:
        session = Session()
        case = session.query(Results).filter_by(id=case_to_update.id).first()
        case.status = case_to_update.status
        session.commit()
        session.close()
        return True
    except:
        helper.log('critical','db',"unable to update case status")
    return False

## Delete specific case from database ##########
def delete_case(id):
    try:
        session = Session()
        case = session.query(Results).filter_by(id=id).first()
        session.delete(case)
        session.commit()
        helper.log('critical','db',"case record deleted successfully")
        session.close()
        return True
    except:
        helper.log('critical','db',"unable to delete case")
    return False

## Read users from database ##########
def read_users():
    session = Session()
    all_users = session.query(User.id, User.first_name, User.last_name, User.username, User.email, User.password, User.role, User.created_at).all()
    session.close()
    return all_users

## Delete specific user from database ##########
def delete_user(id):
    try:
        session = Session()
        user = session.query(User).filter_by(id=id).first()
        session.delete(user)
        session.commit()
        helper.log('critical','db',"user record deleted successfully")
        session.close()
        return True
    except:
        helper.log('critical','db',"unable to delete user")
    return False
#### these last two need to be edited

##  Read specific user from database ##########
def user_update(user_id):
    helper.log('critical','db',"trying to get case status")
    session = Session()
    user_to_update = session.query(User).filter_by(id=user_id).first()
    session.close()
    if user_to_update is None:
        helper.log('critical','db',"no such case")
        return "None"
    elif user_to_update is not None:
        return user_to_update
    return "None"

## Save updated user info into database ##########
def update_user_to_db(user_to_update):
    try:
        session = Session()
        user = session.query(User).filter_by(id=user_to_update.id).first()
        user.first_name = str(user_to_update.first_name)
        user.last_name = str(user_to_update.last_name)
        user.username = str(user_to_update.username)
        user.email = str(user_to_update.email)
        user.password = str(user_to_update.password)
        user.role = str(user_to_update.role)
        session.commit()
        helper.log('critical','db',"user data updated")
        session.close()
        return True
    except Exception as E:
        print(E)
        helper.log('critical','db',"unable to update user info")
    return False

## Count total number of users ###############
def count_users():
    session = Session()
    users = session.query(User).count()
    helper.log('critical','db',"all users counted")
    session.close()
    return users

## Count total number of cases ###############
def count_cases():
    session = Session()
    cases = session.query(Results).count()
    helper.log('critical','db',"all users counted")
    session.close()
    return cases

## Count total number of solved/closed cases ###############
def count_closed_cases():
    session = Session()
    cases = session.query(Results).filter_by(status="Closed").count()
    helper.log('critical','db',"all users counted")
    session.close()
    return cases