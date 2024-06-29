from app import bcrypt, login_manager
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin
from typing import List,Optional
from db import session
from db import engine
from flask import flash,redirect

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

    def add_balance(self, amount):
        self.wallet += amount
        session.commit()
        flash(f'₹ {amount:.2f} Added Successfully to you wallet. Available Balance: {self.wallet}', category='success')


    def deduct_balance(self, amount):
        if self.wallet < amount:
            flash('Not Enough Balance. Kindly add to continue')
            return redirect('recharge_wallet_page')
        else:
            self.wallet -= amount
            session.commit()
            flash(f'Transaction Complete. New Balance: {self.wallet:.2f}', category='success')


class Sponsor(Base):
    __tablename__ = 'sponsors'
    id: Mapped[int] = mapped_column(primary_key=True)
    sponsor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='sponsor')
    sponsor_type: Mapped[str] = mapped_column(
        nullable=False, default='individual')
    industry: Mapped[str] = mapped_column(
        nullable=False, default='others')
    
    ad_requests: Mapped[List['AdRequest']] = relationship(
        back_populates='sponsor')
    

class Influencer(Base):
    __tablename__ = 'influencers'
    id: Mapped[int] = mapped_column(primary_key=True)
    influencer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='influencer')
    category: Mapped[str] = mapped_column(nullable=False)
    niche: Mapped[str] = mapped_column(nullable=False)
    reach: Mapped[int] = mapped_column(nullable=False, default=1)

    rating: Mapped[int] = mapped_column(nullable=False, default=5)
    finished_campaigns:Mapped[int] = mapped_column(nullable=False, default=0)


    active_campaigns: Mapped[List['Campaign']] = relationship(
        back_populates='assigned_to')
    
    ad_requests: Mapped[List['AdRequest']] = relationship(
        back_populates='influencer')



class AdRequest(Base):  # Sent by Sponsor
    __tablename__ = 'ad_requests'
    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign: Mapped['Campaign'] = relationship(back_populates='ad_requests')

    influencer_id: Mapped[int] = mapped_column(ForeignKey('influencers.id'))
    influencer: Mapped['Influencer'] = relationship(
        back_populates='ad_requests')
    
    sponsor_id: Mapped[int] = mapped_column(ForeignKey('sponsors.id'))
    sponsor: Mapped['Sponsor'] = relationship(
        back_populates='ad_requests')

    messages: Mapped[str] = mapped_column(nullable=False)
    requirements: Mapped[str] = mapped_column(nullable=False, default='')
    payment_amount: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(nullable=False, default='Pending')


class CampaignRequest(Base):  # Sent by Influencer
    __tablename__ = 'campaign_requests'
    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    campaign: Mapped['Campaign'] = relationship(
        back_populates='campaign_requests')

    influencer_id: Mapped[int] = mapped_column(ForeignKey('influencers.id'))
    messages: Mapped[str] = mapped_column(nullable=False)
    requirements: Mapped[str]
    payment_amount: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(nullable=False, default='Pending')


class Campaign(Base):
    __tablename__ = 'campaigns'
    id: Mapped[int] = mapped_column(primary_key=True)

    ad_requests: Mapped[List['AdRequest']] = relationship(
        back_populates='campaign')

    campaign_requests: Mapped[List['CampaignRequest']] = relationship(
        back_populates='campaign')

    sponsor_id: Mapped[int] = mapped_column(ForeignKey('sponsors.id'))

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=False, unique=True)
    start_date: Mapped[str] = mapped_column(
        nullable=False, default='01-01-2024')
    end_date: Mapped[str] = mapped_column(
        nullable=False, default='01-01-2024')
    cost: Mapped[int] = mapped_column(nullable=False, default=0)
    visibility: Mapped[bool] = mapped_column(
        nullable=False, default=True)  # False - Private
    # True - Public

    goals: Mapped[str]

    category: Mapped[str] = mapped_column(nullable=False)
    progress: Mapped[int] = mapped_column(nullable=False,default=0)

    # is_active:Mapped[bool] = mapped_column(nullable=False, default=False)
    influencer_id:Mapped[Optional[int]] = mapped_column(ForeignKey('influencers.id'))
    assigned_to:Mapped[Optional['Influencer']] = relationship(
        back_populates='active_campaigns')
    

    status: Mapped[str] = mapped_column(nullable=False, default='Incomplete')
    secret_code: Mapped[str] = mapped_column(
        nullable=False, default='')
    checkpoint_weights: Mapped[str] = mapped_column(
        nullable=False, default='')
    spare:Mapped[int]=mapped_column(nullable=False,default=0)




session.rollback()
Base.metadata.create_all(engine)