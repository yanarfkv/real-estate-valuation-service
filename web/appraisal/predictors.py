import os
import catboost
from scipy.special import inv_boxcox

from web import settings


model_path = os.path.join(settings.BASE_DIR, 'appraisal', 'static', 'models', 'catboost.cbm')
model = catboost.CatBoostRegressor()
model.load_model(model_path)


class PredictionService:
    price_lambda = -0.08893267797771671

    @staticmethod
    def make_prediction(features):
        prediction_result = model.predict([features])
        return inv_boxcox(prediction_result[0], PredictionService.price_lambda)
