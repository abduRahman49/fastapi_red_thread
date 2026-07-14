import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from app.models.user import User
from app.models.experiment import Experiment
from app.core.security import hash_password


fake = Faker("fr_FR")

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"
    
    username = factory.LazyFunction(lambda: fake.user_name())
    email = factory.LazyFunction(lambda: fake.email())
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
    is_active = True


class ExperimentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Experiment
        sqlalchemy_session_persistence = "flush"
    
    name = factory.LazyFunction(lambda: f"exp_{fake.word()}")
    algorithm = factory.Iterator(
        ["random_forest", "xgboost", "neural_network"]
    )
    status = "pending"
    owner = factory.SubFactory(UserFactory)
