from app import bcrypt, login_manager
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin
from typing import List
from db import session

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

class Base(DeclarativeBase):
    pass


class User(Base, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    username: Mapped[str] = mapped_column(nullable=False)
    email_address: Mapped[str] = mapped_column(unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(nullable=False)
    wallet: Mapped[int] = mapped_column(nullable=False, default=1000)
    currently_logged_in_as: Mapped[bool] = mapped_column(nullable=False, default=False)
    # False => influencer, True => Sponsor
    is_sponsor: Mapped[bool] = mapped_column(nullable=False, default=False)
    sponsor: Mapped['Sponsor'] = relationship(back_populates='user')
    is_influencer: Mapped[bool] = mapped_column(nullable=False, default=False)
    influencer: Mapped['Influencer'] = relationship(
        back_populates='user')

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self,password_unhashed):
        self.password_hash=bcrypt.generate_password_hash(password_unhashed).decode('utf-8')

    @property
    def role(self):
        return self.role

    @role.setter
    def role(self, role):
        if role == 'influencer':
            self.is_influencer = True
        if role == 'sponsor':
            self.is_sponsor = True

    @property
    def current_role(self):
        return self.role

    @role.setter
    def current_role(self, role):
        self.currently_logged_in_as= (role == 'sponsor')
    
    def is_password_correct(self,entered_password):
        return bcrypt.check_password_hash(self.password_hash,entered_password)


class Sponsor(Base):
    __tablename__ = 'sponsors'
    id: Mapped[int] = mapped_column(primary_key=True)
    sponsor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='sponsor')
    sponsor_type: Mapped[str] = mapped_column(
        nullable=False, default='Individual')


class Influencer(Base):
    __tablename__ = 'influencers'
    id: Mapped[int] = mapped_column(primary_key=True)
    influencer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='influencer')
    category: Mapped[str] = mapped_column(nullable=False)
    niche: Mapped[str] = mapped_column(nullable=False)
    reach: Mapped[int] = mapped_column(nullable=False, default=1)


class Ad_Request(Base):  # Sent by Sponsor
    __tablename__ = 'ad_requests'
    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign: Mapped['Campaign'] = relationship(back_populates='ad_requests')

    influencer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    messages: Mapped[str] = mapped_column(nullable=False)
    requirements: Mapped[str]
    payment_amount: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(nullable=False, default='Pending')


class Campaign_Request(Base):  # Sent by Influencer
    __tablename__ = 'campaign_requests'
    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign: Mapped['Campaign'] = relationship(
        back_populates='campaign_requests')

    influencer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    messages: Mapped[str] = mapped_column(nullable=False)
    requirements: Mapped[str]
    payment_amount: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(nullable=False, default='Pending')


class Campaign(Base):
    __tablename__ = 'campaigns'
    id: Mapped[int] = mapped_column(primary_key=True)

    ad_requests: Mapped[List['Ad_Request']] = relationship(
        back_populates='campaign')

    campaign_requests: Mapped[List['Campaign_Request']] = relationship(
        back_populates='campaign')

    sponsor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    decription: Mapped[str] = mapped_column(nullable=False, unique=True)
    start_date: Mapped[str] = mapped_column(
        nullable=False, default='01-01-2024')
    end_date: Mapped[str] = mapped_column(
        nullable=False, default='01-01-2024')
    cost: Mapped[int] = mapped_column(nullable=False, default=0)
    visibility: Mapped[bool] = mapped_column(
        nullable=False, default=True)  # False - Private
    # True - Public
    goals: Mapped[str]
