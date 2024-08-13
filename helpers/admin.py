from db import session
from models import User, Campaign,CampaignRequest,AdRequest,RedeemRequest
import re
from sqlalchemy import func
import datetime


def parse_date(text):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.datetime.strptime(
                text, fmt)
        except ValueError:
            pass

def user_metrics(query_user):
    users=query_user.all()
    banned_users=0
    for user in users:
        if parse_date(
            user.banned_till) > datetime.datetime.now():
            banned_users=banned_users+1
        
    user_cnt = query_user.count()
    sponsor_cnt = query_user.filter(User.is_sponsor).count()
    influencer_cnt = query_user.filter(User.is_influencer).count()
    
    sponsor_ratio = sponsor_cnt/user_cnt
    influencer_ratio = influencer_cnt/user_cnt
    return {
        'user_cnt': user_cnt, 
        'sponsor_ratio': sponsor_ratio, 
        'influencer_ratio': influencer_ratio,
        'sponsor_cnt': sponsor_cnt,
        'influencer_cnt': influencer_cnt,
        'banned_users': banned_users
    }


def campaign_metrics(query_campaign):
    campaign_cnt=query_campaign.count()
    public_cnt = query_campaign.filter(Campaign.visibility).count()
    public_ratio=public_cnt/campaign_cnt
    
    category_cnt = session.query(
        Campaign.category, func.count(Campaign.category)).group_by(Campaign.category).all()

    category_cnt_label = [key for key, value in category_cnt]
    category_cnt_data = [value for key, value in category_cnt]

    category_cost = session.query(
        Campaign.category, func.sum(Campaign.cost)).group_by(Campaign.category).all()
    category_cost_label = [key for key, value in category_cost]
    category_cost_data = [value for key, value in category_cost]

    category_avg = session.query(
        Campaign.category, func.avg(Campaign.cost)).group_by(Campaign.category).all()
    category_avg_label = [key for key, value in category_avg]
    category_avg_data = [value for key, value in category_avg]

    
    return {
        'campaign_cnt':campaign_cnt,
        'public_cnt': public_cnt,
        'public_ratio': public_ratio,
        'category_cnt_label': category_cnt_label,
        'category_cnt_data': category_cnt_data,
        'category_cost_label': category_cost_label,
        'category_cost_data': category_cost_data, 
        'category_avg_label': category_avg_label,
        'category_avg_data': category_avg_data
        }


def request_metrics():
    campaign_request_count= session.query(CampaignRequest).count()
    ad_request_count = session.query(AdRequest).count()
    return {
        'campaign_request_count': campaign_request_count,
        'ad_request_count': ad_request_count
    }


def redeem_request():
    query_user = session.query(RedeemRequest).filter(RedeemRequest.status=='pending')
    return query_user.count()


def compile_metrics():
    query_user = session.query(User)
    user_metric = user_metrics(query_user)
    query_campaign = session.query(Campaign)
    campaign_metric=campaign_metrics(query_campaign)
    return {
        'user_metrics':user_metric,
        'campaign_metrics':campaign_metric,
        'request_metrics': request_metrics(),
        'redeem_request': redeem_request()
    }
