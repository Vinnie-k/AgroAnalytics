import os
import json
import logging
from openai import OpenAI
from models import User, AgriculturalData

class ChatbotService:
    """AI Chatbot service for agricultural assistance using OpenAI"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "default_openai_key":
            logging.error("No valid OpenAI API key found")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        
    def get_response(self, message, user):
        """Get AI chatbot response for farmer queries"""
        try:
            if not self.openai_client:
                return "I'm sorry, but the AI chatbot service is temporarily unavailable. Please try again later or contact support."
            # Prepare context about the user and their farm
            user_context = self._prepare_user_context(user)
            
            # Create system prompt for agricultural assistance
            system_prompt = f"""
            You are an expert agricultural advisor for Kenyan farmers. Your role is to provide 
            practical, accurate, and helpful advice about farming in Kenya.
            
            User Context:
            - Farmer Name: {user.full_name}
            - Location: {user.county} County, Kenya
            - Farm Size: {user.farm_size} acres
            - Primary Crops: {user_context['crops']}
            - Farming Experience: {user.farming_experience} years
            
            Guidelines:
            1. Provide specific advice relevant to Kenyan agriculture
            2. Consider local climate, soil conditions, and market factors
            3. Suggest appropriate crops for their region and farm size
            4. Include information about local agricultural practices
            5. Be encouraging and supportive
            6. If asked about prices or market data, mention checking with local markets
            7. Always respond in a friendly, professional manner
            8. Keep responses concise but informative (maximum 200 words)
            """
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Chatbot response error: {str(e)}")
            return self._get_fallback_response(message)
    
    def _prepare_user_context(self, user):
        """Prepare user context for chatbot"""
        try:
            crops = json.loads(user.primary_crops) if user.primary_crops else []
            return {
                'crops': ', '.join(crops) if crops else 'Various crops',
                'county': user.county,
                'farm_size': user.farm_size or 'Not specified',
                'experience': user.farming_experience or 'Not specified'
            }
        except:
            return {
                'crops': 'Various crops',
                'county': user.county or 'Kenya',
                'farm_size': 'Not specified',
                'experience': 'Not specified'
            }
    
    def _get_fallback_response(self, message):
        """Provide fallback responses when AI service is unavailable"""
        message_lower = message.lower()
        
        # Common farming questions and responses
        if any(word in message_lower for word in ['maize', 'corn']):
            return """
            Maize is Kenya's staple crop. For best results:
            - Plant during long rains (March-May) or short rains (October-December)
            - Use certified seeds and proper spacing
            - Apply fertilizer at planting and top-dress after 6 weeks
            - Control weeds early and monitor for pests like fall armyworm
            """
        
        elif any(word in message_lower for word in ['beans', 'legumes']):
            return """
            Beans are excellent for soil fertility and nutrition:
            - Choose varieties suited to your altitude and rainfall
            - Plant with maize for intercropping benefits
            - No need for nitrogen fertilizer as beans fix nitrogen
            - Harvest when pods are dry to avoid storage problems
            """
        
        elif any(word in message_lower for word in ['fertilizer', 'nutrients']):
            return """
            Proper fertilization is key to good yields:
            - Test your soil to know nutrient needs
            - Apply organic matter like compost or manure
            - Use DAP fertilizer at planting for phosphorus
            - Top-dress with CAN or urea for nitrogen
            - Time application with rainfall for best results
            """
        
        elif any(word in message_lower for word in ['weather', 'rain', 'drought']):
            return """
            Weather management is crucial in Kenyan agriculture:
            - Monitor weather forecasts from Kenya Meteorological Department
            - Practice water conservation during dry periods
            - Choose drought-resistant varieties in arid areas
            - Use mulching to retain soil moisture
            - Consider irrigation if water is available
            """
        
        elif any(word in message_lower for word in ['price', 'market', 'sell']):
            return """
            Getting good prices for your produce:
            - Check prices at multiple markets before selling
            - Consider value addition like drying or processing
            - Join farmer groups for better bargaining power
            - Time your sales to avoid harvest gluts
            - Store properly to sell during lean seasons
            """
        
        elif any(word in message_lower for word in ['pest', 'disease']):
            return """
            Pest and disease management:
            - Practice crop rotation to break pest cycles
            - Scout your fields regularly for early detection
            - Use integrated pest management (IPM) approaches
            - Apply pesticides only when necessary and safely
            - Consult agricultural extension officers for severe problems
            """
        
        else:
            return """
            I'm here to help with your farming questions! You can ask me about:
            - Crop selection and planting advice
            - Fertilizer and soil management
            - Pest and disease control
            - Weather and climate considerations
            - Market and pricing information
            - General farming best practices for Kenya
            
            What specific farming challenge can I help you with?
            """
    
    def get_crop_advice(self, crop_name, user):
        """Get specific advice for a particular crop"""
        try:
            prompt = f"""
            Provide detailed growing advice for {crop_name} in {user.county} County, Kenya.
            Consider the local climate, soil conditions, and farming practices.
            Include planting, care, and harvesting advice.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert agricultural advisor specializing in Kenyan farming."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Crop advice error: {str(e)}")
            return f"Here are general tips for growing {crop_name} in Kenya: Choose appropriate varieties, prepare land well, plant at the right time, manage nutrients and water, and control pests and diseases."
    
    def get_market_insights(self, user):
        """Get market insights for user's location and crops"""
        try:
            user_crops = json.loads(user.primary_crops) if user.primary_crops else ['maize', 'beans']
            
            prompt = f"""
            Provide market insights and trends for these crops in {user.county} County, Kenya:
            {', '.join(user_crops)}
            
            Include general price trends, best selling seasons, and marketing tips.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an agricultural market analyst for Kenya."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Market insights error: {str(e)}")
            return "Market prices vary by season and location. Check with local markets, join farmer groups for better prices, and consider value addition to increase profits."
