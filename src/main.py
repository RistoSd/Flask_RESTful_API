from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

app = Flask(__name__)
api = Api(app)
engine = sqlalchemy.create_engine(
    'mariadb+mariadbconnector://root:karu@localhost/project_user')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+mariadbconnector://root:karu@localhost/project_user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Base = declarative_base()
db = sqlalchemy
Session = sessionmaker(bind=engine)
session = Session()

project_user = db.Table('project_user',
                        Base.metadata,
                        db.Column('project_id', db.Integer,
                                  db.ForeignKey('project.id')),
                        db.Column('user_id', db.Integer,
                                  db.ForeignKey('user.id')),
                        )


class Projectmodel(Base):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    participating = relationship(
        'Usermodel', secondary=project_user, backref='users')

    def __repr__(self):
        return f'<Project: {self.name}>'


class Usermodel(Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __repr__(self):
        return f'<User: {self.name}>'


project_put_args = reqparse.RequestParser()
project_put_args.add_argument(
    "name", type=str, help="Name of the project is required", required=True)
project_put_args.add_argument("user_name", type=str, help="Project users")

project_update_args = reqparse.RequestParser()
project_update_args.add_argument(
    "name", type=str, help="Name of the project is required")
project_update_args.add_argument("user_name", type=str, help="Project users")

user_put_args = reqparse.RequestParser()
user_put_args.add_argument(
    "name", type=str, help="Name of the user is required", required=True)


resource_fields = {
    'id': fields.Integer,
    'name': fields.String, }


def user_list_template(project):
    user_list = []
    for user in project.participating:
        user_list.append(user.name)
    return user_list


class Project(Resource):
    def get(self, project_id):
        result = session.query(Projectmodel).filter_by(id=project_id).first()
        if not result:
            abort(404, message="Could not find project with that id...")
        user_list = user_list_template(result)
        return {"id": project_id, "name": result.name, "project_users": user_list}

    def put(self, project_id):
        args = project_put_args.parse_args()
        user_name = args['user_name']
        project_result = session.query(
            Projectmodel).filter_by(id=project_id).first()
        if project_result:
            abort(409, message="Project id taken...")
        project = Projectmodel(id=project_id, name=args['name'])
        if user_name:
            user_result = session.query(
                Usermodel).filter_by(name=user_name).first()
            if not user_result:
                user_result = Usermodel(name=user_name)
            project.participating.append(user_result)
        user_list = user_list_template(project)
        session.add(project)
        session.commit()
        return {"id": project_id, "name": project.name, "project_users": user_list}

    def patch(self, project_id):
        args = project_update_args.parse_args()
        result = session.query(Projectmodel).filter_by(id=project_id).first()
        if not result:
            abort(404, message="Project doesn't exist, cannot update")
        user_name = args['user_name']
        user_result = session.query(
            Usermodel).filter_by(name=user_name).first()
        user_list = user_list_template(result)
        if user_result:
            user = user_result
        elif not user_result:
            user = Usermodel(name=user_name)
        if result.participating:
            if user_name in user_list:
                result.participating.remove(user)
            elif user_name not in user_list:
                result.participating.append(user)
        elif not result.participating:
            result.participating.append(user)
        if args['name']:
            result.name = args['name']
        user_list = user_list_template(result)
        session.commit()
        return {"id": project_id, "name": result.name, "project_users": user_list}

    def delete(self, project_id):
        result = session.query(Projectmodel).filter_by(id=project_id).first()
        if not result:
            abort(404, message="Project id not found")
        result.participating.clear()
        session.delete(result)
        session.commit()
        return {"message":"Project has been deleted"}


class User(Resource):
    @marshal_with(resource_fields)
    def put(self, user_id):
        args = user_put_args.parse_args()
        result = session.query(Usermodel).filter_by(id=user_id).first()
        if result:
            abort(409, message="User id taken...")
        user = Usermodel(id=user_id, name=args['name'])
        session.add(user)
        session.commit()
        return user, 201

    @marshal_with(resource_fields)
    def get(self, user_id):
        result = session.query(Usermodel).all()
        if not result:
            abort(404, message="No users found...")
        return result

    @marshal_with(resource_fields)
    def delete(self, user_id):
        result = session.query(Usermodel).filter_by(id=user_id).first()
        if not result:
            abort(404, message="Project id not found")
        session.delete(result)
        session.commit()
        return "Project has been deleted"


api.add_resource(Project, "/project/<int:project_id>")
api.add_resource(User, "/user/<int:user_id>")

if __name__ == "__main__":
    app.run(debug=True)
