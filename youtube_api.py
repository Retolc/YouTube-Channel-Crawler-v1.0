# youtube_api.py (Versão Otimizada)
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime, timedelta
import time
from dateutil import parser
from datetime import datetime, timedelta, timezone
import requests
from PIL import Image
import io
import data_handler


class ShortsDetector:
    """Detector de Shorts usando múltiplos métodos"""
    


    # ✅ LISTA ÚNICA para detecção E contagem
    SHORTS_KEYWORDS = [
        # Inglês
        'shorts', '#shorts', 'short video', 'short form', 'short-form',
        'tiktok', 'tiktoks', 'reels', 'reel', 'vertical video',
        '60 seconds', 'under 60', 'under 1 minute',
        '#short', 'short content', 'shorts channel', 'shortfilm',
        
        # Português
        'vídeo curto', 'vídeos curtos', 'shorts brasileiro',
        'video curto', 'videos curtos',
        
        # Espanhol
        'corto', 'cortos', 'video corto',
        
        # Japonês/Chinês
        '短編', '短视频', '短動画', 'ショート', '短片'
    ]
    
    @staticmethod
    def detect_shorts_keywords(text):
        """Detecta shorts por keywords - VERSÃO UNIFICADA"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for keyword in ShortsDetector.SHORTS_KEYWORDS:
            if keyword in text_lower:
                return True
        
        # Palavras isoladas
        words = text_lower.split()
        return 'shorts' in words or '#shorts' in words
    
    @staticmethod
    def count_shorts_mentions(text):
        """Conta menções de shorts - VERSÃO UNIFICADA"""
        if not text:
            return 0
        
        text_lower = text.lower()
        count = 0
        
        # Contar cada keyword
        for keyword in ShortsDetector.SHORTS_KEYWORDS:
            count += text_lower.count(keyword)
        
        # Contar palavras isoladas também
        words = text_lower.split()
        count += words.count('shorts')
        count += words.count('#shorts')
        
        return count



    @staticmethod
    def is_shorts_by_url(video_id):
        """Método URL Pattern - VERSÃO FUNCIONAL"""
        try:
            shorts_url = f"https://www.youtube.com/shorts/{video_id}"
            response = requests.head(shorts_url, timeout=3, allow_redirects=True)
            
            # ✅ CORREÇÃO: Verifica múltiplos cenários
            # 1. URL direta funciona (status 200)
            # 2. Redireciona mas a URL final contém /shorts/
            final_url = response.url if hasattr(response, 'url') else shorts_url
            
            # Se a URL final contém "/shorts/", é um shorts
            is_shorts = '/shorts/' in final_url
            return is_shorts
                
        except Exception as e:
            return False


    @staticmethod
    def detect_shorts_keywords(text):
        """Detecta keywords de shorts com matching mais inteligente"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Keywords mais abrangentes (incluir variações)
        shorts_keywords = [
            # Inglês
            'shorts', '#shorts', 'short video', 'short form',
            'tiktok', 'reels', 'reel', 'vertical video',
            '60 seconds', 'under 60', 'under 1 minute',
            '#short', 'short content', 'shorts channel',
            
            # Português
            'vídeo curto', 'vídeos curtos', 'shorts brasileiro',
            
            # Espanhol
            'corto', 'cortos', 'video corto',
            
            # Japonês/Chinês
            '短編', '短视频', '短動画', 'ショート'
        ]
        
        # Verificar presença de qualquer keyword
        for keyword in shorts_keywords:
            if keyword in text_lower:
                return True
        
        # Verificar padrões como "shorts" isolado
        words = text_lower.split()
        if 'shorts' in words or '#shorts' in words:
            return True
        
        return False










    @staticmethod
    def get_video_duration(youtube_api, video_id):
        """
        Método 3: Duração via API (custo: 1 unidade)
        Retorna duração em segundos - VERSÃO COM LOG DIAGNÓSTICO
        """
        try:

            video_response = youtube_api.youtube.videos().list(
                id=video_id,
                part='contentDetails'
            ).execute()

            youtube_api.quota_used += 1

            if video_response.get('items'):
                duration_iso = video_response['items'][0]['contentDetails']['duration']
                seconds = ShortsDetector._parse_duration_iso(duration_iso)
                return seconds
            else:
                return None

        except Exception as e:
            return None

    

    
    @staticmethod
    def _parse_duration_iso(duration):
        """Converte QUALQUER formato de duração do YouTube para segundos - VERSÃO MELHORADA"""
        import re
        
        original_duration = duration
        
        # 1. Remove prefixo "PT" ou "P" se existir
        if duration.startswith('PT'):
            duration = duration[2:]
        elif duration.startswith('P'):
            duration = duration[1:]
        
        # 2. Caso óbvio: duração zero ou vazia
        if duration in ('0D', '') or not duration:
            return 0
        
        total_seconds = 0
        parsed_anything = False
        
        # 3. Extrai horas
        hour_match = re.search(r'(\d+)H', duration)
        if hour_match:
            total_seconds += int(hour_match.group(1)) * 3600
            parsed_anything = True
            # Remove a parte das horas para facilitar a análise do restante
            duration = duration.replace(hour_match.group(0), '', 1)
        
        # 4. Extrai minutos (pode ser 'M' explícito ou número após H sem unidade)
        minute_match = re.search(r'(\d+)M', duration)
        if minute_match:
            total_seconds += int(minute_match.group(1)) * 60
            parsed_anything = True
        else:
            # CASO "1H20": Após remover "1H", sobra "20". Isso são minutos.
            # Se houver números restantes sem unidade, assumimos minutos.
            remaining_numbers = re.search(r'^(\d+)$', duration)
            if remaining_numbers:
                total_seconds += int(remaining_numbers.group(1)) * 60
                parsed_anything = True
        
        # 5. Extrai segundos (sempre com 'S')
        second_match = re.search(r'(\d+)S', duration)
        if second_match:
            total_seconds += int(second_match.group(1))
            parsed_anything = True
        
        # Se não conseguiu parsear nada, retorna o valor raw original
        if not parsed_anything:
            return original_duration
        
        return total_seconds



class YouTubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.quota_used = 0
        self.cache = {}
        self.data_handler = data_handler
        
        # Novo: detector de shorts
        self.shorts_detector = ShortsDetector()
        
        # Cache de busca
        self.search_cache = {}



    COUNTRIES_MAP = {
        'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AF': 'Afghanistan',
        'AG': 'Antigua and Barbuda', 'AI': 'Anguilla', 'AL': 'Albania',
        'AM': 'Armenia', 'AO': 'Angola', 'AQ': 'Antarctica',
        'AR': 'Argentina', 'AS': 'American Samoa', 'AT': 'Austria',
        'AU': 'Australia', 'AW': 'Aruba', 'AX': 'Åland Islands',
        'AZ': 'Azerbaijan', 'BA': 'Bosnia and Herzegovina', 'BB': 'Barbados',
        'BD': 'Bangladesh', 'BE': 'Belgium', 'BF': 'Burkina Faso',
        'BG': 'Bulgaria', 'BH': 'Bahrain', 'BI': 'Burundi',
        'BJ': 'Benin', 'BL': 'Saint Barthélemy', 'BM': 'Bermuda',
        'BN': 'Brunei Darussalam', 'BO': 'Bolivia', 'BQ': 'Bonaire',
        'BR': 'Brazil', 'BS': 'Bahamas', 'BT': 'Bhutan',
        'BV': 'Bouvet Island', 'BW': 'Botswana', 'BY': 'Belarus',
        'BZ': 'Belize', 'CA': 'Canada', 'CC': 'Cocos Islands',
        'CD': 'Congo', 'CF': 'Central African Republic', 'CG': 'Congo',
        'CH': 'Switzerland', 'CI': "Côte d'Ivoire", 'CK': 'Cook Islands',
        'CL': 'Chile', 'CM': 'Cameroon', 'CN': 'China',
        'CO': 'Colombia', 'CR': 'Costa Rica', 'CU': 'Cuba',
        'CV': 'Cabo Verde', 'CW': 'Curaçao', 'CX': 'Christmas Island',
        'CY': 'Cyprus', 'CZ': 'Czechia', 'DE': 'Germany',
        'DJ': 'Djibouti', 'DK': 'Denmark', 'DM': 'Dominica',
        'DO': 'Dominican Republic', 'DZ': 'Algeria', 'EC': 'Ecuador',
        'EE': 'Estonia', 'EG': 'Egypt', 'EH': 'Western Sahara',
        'ER': 'Eritrea', 'ES': 'Spain', 'ET': 'Ethiopia',
        'FI': 'Finland', 'FJ': 'Fiji', 'FK': 'Falkland Islands',
        'FM': 'Micronesia', 'FO': 'Faroe Islands', 'FR': 'France',
        'GA': 'Gabon', 'GB': 'United Kingdom', 'GD': 'Grenada',
        'GE': 'Georgia', 'GF': 'French Guiana', 'GG': 'Guernsey',
        'GH': 'Ghana', 'GI': 'Gibraltar', 'GL': 'Greenland',
        'GM': 'Gambia', 'GN': 'Guinea', 'GP': 'Guadeloupe',
        'GQ': 'Equatorial Guinea', 'GR': 'Greece', 'GS': 'South Georgia',
        'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinea-Bissau',
        'GY': 'Guyana', 'HK': 'Hong Kong', 'HM': 'Heard Island',
        'HN': 'Honduras', 'HR': 'Croatia', 'HT': 'Haiti',
        'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland',
        'IL': 'Israel', 'IM': 'Isle of Man', 'IN': 'India',
        'IO': 'British Indian Ocean Territory', 'IQ': 'Iraq',
        'IR': 'Iran', 'IS': 'Iceland', 'IT': 'Italy',
        'JE': 'Jersey', 'JM': 'Jamaica', 'JO': 'Jordan',
        'JP': 'Japan', 'KE': 'Kenya', 'KG': 'Kyrgyzstan',
        'KH': 'Cambodia', 'KI': 'Kiribati', 'KM': 'Comoros',
        'KN': 'Saint Kitts and Nevis', 'KP': 'North Korea',
        'KR': 'South Korea', 'KW': 'Kuwait', 'KY': 'Cayman Islands',
        'KZ': 'Kazakhstan', 'LA': 'Lao', 'LB': 'Lebanon',
        'LC': 'Saint Lucia', 'LI': 'Liechtenstein', 'LK': 'Sri Lanka',
        'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Lithuania',
        'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya',
        'MA': 'Morocco', 'MC': 'Monaco', 'MD': 'Moldova',
        'ME': 'Montenegro', 'MF': 'Saint Martin', 'MG': 'Madagascar',
        'MH': 'Marshall Islands', 'MK': 'North Macedonia', 'ML': 'Mali',
        'MM': 'Myanmar', 'MN': 'Mongolia', 'MO': 'Macao',
        'MP': 'Northern Mariana Islands', 'MQ': 'Martinique',
        'MR': 'Mauritania', 'MS': 'Montserrat', 'MT': 'Malta',
        'MU': 'Mauritius', 'MV': 'Maldives', 'MW': 'Malawi',
        'MX': 'Mexico', 'MY': 'Malaysia', 'MZ': 'Mozambique',
        'NA': 'Namibia', 'NC': 'New Caledonia', 'NE': 'Niger',
        'NF': 'Norfolk Island', 'NG': 'Nigeria', 'NI': 'Nicaragua',
        'NL': 'Netherlands', 'NO': 'Norway', 'NP': 'Nepal',
        'NR': 'Nauru', 'NU': 'Niue', 'NZ': 'New Zealand',
        'OM': 'Oman', 'PA': 'Panama', 'PE': 'Peru',
        'PF': 'French Polynesia', 'PG': 'Papua New Guinea',
        'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Poland',
        'PM': 'Saint Pierre and Miquelon', 'PN': 'Pitcairn',
        'PR': 'Puerto Rico', 'PS': 'Palestine', 'PT': 'Portugal',
        'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar',
        'RE': 'Réunion', 'RO': 'Romania', 'RS': 'Serbia',
        'RU': 'Russia', 'RW': 'Rwanda', 'SA': 'Saudi Arabia',
        'SB': 'Solomon Islands', 'SC': 'Seychelles', 'SD': 'Sudan',
        'SE': 'Sweden', 'SG': 'Singapore', 'SH': 'Saint Helena',
        'SI': 'Slovenia', 'SJ': 'Svalbard and Jan Mayen',
        'SK': 'Slovakia', 'SL': 'Sierra Leone', 'SM': 'San Marino',
        'SN': 'Senegal', 'SO': 'Somalia', 'SR': 'Suriname',
        'SS': 'South Sudan', 'ST': 'Sao Tome and Principe',
        'SV': 'El Salvador', 'SX': 'Sint Maarten', 'SY': 'Syria',
        'SZ': 'Eswatini', 'TC': 'Turks and Caicos Islands',
        'TD': 'Chad', 'TF': 'French Southern Territories',
        'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tajikistan',
        'TK': 'Tokelau', 'TL': 'Timor-Leste', 'TM': 'Turkmenistan',
        'TN': 'Tunisia', 'TO': 'Tonga', 'TR': 'Turkey',
        'TT': 'Trinidad and Tobago', 'TV': 'Tuvalu', 'TW': 'Taiwan',
        'TZ': 'Tanzania', 'UA': 'Ukraine', 'UG': 'Uganda',
        'UM': 'United States Minor Outlying Islands', 'US': 'United States',
        'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VA': 'Vatican City',
        'VC': 'Saint Vincent and the Grenadines', 'VE': 'Venezuela',
        'VG': 'Virgin Islands (British)', 'VI': 'Virgin Islands (U.S.)',
        'VN': 'Vietnam', 'VU': 'Vanuatu', 'WF': 'Wallis and Futuna',
        'WS': 'Samoa', 'YE': 'Yemen', 'YT': 'Mayotte',
        'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe',
        '': 'Unknown'  # Para códigos vazios
    }




    def get_search_result_details(self, channel_id):
        """Retorna detalhes da busca para um canal específico - CORRIGIDO"""
        if hasattr(self, 'search_results_cache') and channel_id in self.search_results_cache:
            result = self.search_results_cache[channel_id]
            return {
                'channel_id': result.get('channel_id'),
                'video_id': result.get('video_id'),
                'search_video_title': result.get('search_video_title', ''),
                'search_video_published': result.get('search_video_published', ''),
                'search_video_is_shorts_url': result.get('search_video_is_shorts_url', False),
                'search_video_is_shorts_thumb': result.get('search_video_is_shorts_thumb', False),
                'search_video_is_shorts_keyword': result.get('search_video_is_shorts_keyword', False),
                'search_video_shorts_score': result.get('search_video_shorts_score', 0)
            }
        return None



        
    def search_channels_by_keyword(self, keyword, max_results=10, region_code=None, 
                                    language=None, min_duration=None, detect_shorts=True):
        """Busca vídeos e detecta shorts para cada resultado - VERSÃO COMPATÍVEL"""
        
        cache_key = f"{keyword}|{max_results}|{region_code}|{language}|{min_duration}|{detect_shorts}"
        
        if hasattr(self, 'search_cache') and cache_key in self.search_cache:
            cached_results = self.search_cache[cache_key]
            return [r['channel_id'] for r in cached_results]
        
        try:
            results_per_call = min(50, max_results)
            
            params = {
                'q': keyword,
                'part': 'snippet',
                'type': 'video',
                'maxResults': results_per_call,
                'order': 'relevance'
            }
            
            if min_duration == 'medium':
                params['videoDuration'] = 'medium'
            elif min_duration == 'long':
                params['videoDuration'] = 'long'
            elif min_duration == 'short':
                params['videoDuration'] = 'short'
            
            if region_code:
                params['regionCode'] = region_code
            if language:
                params['relevanceLanguage'] = language
            
            search_response = self.youtube.search().list(**params).execute()
            self.quota_used += 100
            
            channel_results = []
            
            for item in search_response.get('items', []):
                channel_id = item['snippet']['channelId']
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # Detecção de shorts na busca
                shorts_info = {}
                if detect_shorts:
                    shorts_info = self._detect_shorts_for_search_video(video_id, snippet)
                
                result_data = {
                    'channel_id': channel_id,
                    'video_id': video_id,
                    'search_video_title': snippet.get('title', ''),
                    'search_video_published': snippet.get('publishedAt', ''),
                    **shorts_info  # Adiciona info de shorts
                }
                channel_results.append(result_data)
            
            # Salvar no cache de busca COMPLETO
            if not hasattr(self, 'search_cache'):
                self.search_cache = {}
            self.search_cache[cache_key] = channel_results
            
            # Salvar também no cache por channel_id para get_search_result_details
            if not hasattr(self, 'search_results_cache'):
                self.search_results_cache = {}
            
            for result in channel_results:
                self.search_results_cache[result['channel_id']] = result
            
            return [r['channel_id'] for r in channel_results]
            
        except HttpError as e:
            return []
        except Exception as e:
            return []







    def _detect_shorts_for_search_video(self, video_id, snippet):
        """Detecta shorts para vídeo da busca (sem custo de quota)"""
        
        # 1. URL Pattern (mais confiável para shorts nativos)
        is_shorts_url = self.shorts_detector.is_shorts_by_url(video_id)
        
        # 3. Keyword detection (backup)
        title = snippet.get('title', '').lower()
        description = snippet.get('description', '').lower()
        
        shorts_keywords = ['shorts', '#shorts', '#short', 'short', 'tiktok', 'reels', '短视频', '短編']
        is_shorts_keyword = any(kw in title or kw in description for kw in shorts_keywords)
        
        return {
            'search_video_is_shorts_url': is_shorts_url,
            'search_video_is_shorts_keyword': is_shorts_keyword,
            'search_video_shorts_score': int(is_shorts_url) * 80 + int(is_shorts_keyword) * 20  
            }









    


    def get_channel_playlists(self, channel_id, max_playlists=10):
        """
        Obtém playlists do canal.
        Retorna: (nomes, contagens)
        Exemplo: 
        nomes = "Receitas Rápidas; Sobremesas Fáceis"
        contagens = "45; 21"
        """
        try:
            playlists_response = self.youtube.playlists().list(
                channelId=channel_id,
                part='snippet,contentDetails',
                maxResults=min(50, max_playlists)
            ).execute()
            
            self.quota_used += 1
            
            names_list = []
            counts_list = []
            
            for item in playlists_response.get('items', []):
                title = item['snippet']['title'].strip()
                video_count = item['contentDetails']['itemCount']
                
                # Limpar para CSV
                title_clean = title.replace(';', ',').replace('"', "'")
                
                names_list.append(title_clean)
                counts_list.append(str(video_count))
            
            # Juntar com ponto e vírgula
            names_str = "; ".join(names_list) if names_list else ""
            counts_str = "; ".join(counts_list) if counts_list else ""
            
            return names_str, counts_str
            
        except Exception as e:
            return "", ""






    def get_channels_details(self, channel_ids, search_shorts_info_map=None):
        """Obtém detalhes completos dos canais (1 unidade por 50 canais)
        
        Args:
            channel_ids: Lista de IDs dos canais
            search_shorts_info_map: Dicionário {channel_id: shorts_info} da busca
        """
        if not channel_ids:
            return []
        
        # Se não foi passado shorts_info_map, tenta buscar do cache interno
        if search_shorts_info_map is None and hasattr(self, 'search_results_cache'):
            search_shorts_info_map = {}
            for channel_id in channel_ids:
                if channel_id in self.search_results_cache:
                    cache_data = self.search_results_cache[channel_id]
                    search_shorts_info_map[channel_id] = {
                        'search_video_is_shorts_url': cache_data.get('search_video_is_shorts_url', False),
                        'search_video_is_shorts_thumb': cache_data.get('search_video_is_shorts_thumb', False),
                        'search_video_is_shorts_keyword': cache_data.get('search_video_is_shorts_keyword', False),
                        'search_video_shorts_score': cache_data.get('search_video_shorts_score', 0)
                    }
        
        channels_data = []
        # Processamento em lotes (batch) de 50 canais
        for i in range(0, len(channel_ids), 50):
            batch_ids = channel_ids[i:i+50]
            
            try:
                # CUSTO DE 1 UNIDADE POR CHAMADA
                channels_response = self.youtube.channels().list(
                    id=','.join(batch_ids),
                    part='snippet,statistics,brandingSettings',
                    maxResults=50
                ).execute()
                
                self.quota_used += 1
                
                for item in channels_response.get('items', []):
                    # Obter info de shorts da busca para este canal específico
                    channel_shorts_info = None
                    if search_shorts_info_map and item['id'] in search_shorts_info_map:
                        channel_shorts_info = search_shorts_info_map[item['id']]
                    
                    # Dados básicos com info de shorts da busca
                    channel_data = self._parse_channel_data(item, channel_shorts_info)
                    channels_data.append(channel_data)
                    
            except Exception as e:
                continue
        
        return channels_data

    


    def _get_last_channel_video_with_shorts(self, channel_id):
        """Último vídeo - VERSÃO GARANTIDA"""
        try:
            activities_response = self.youtube.activities().list(
                channelId=channel_id,
                part='snippet,contentDetails',
                maxResults=1
            ).execute()
            
            self.quota_used += 1
            
            if not activities_response.get('items'):
                return None
                
            item = activities_response['items'][0]
            
            if item['snippet']['type'] != 'upload':
                return None
                
            video_id = item['contentDetails']['upload']['videoId']
            snippet = item['snippet']
            
            duration_seconds = self.shorts_detector.get_video_duration(self, video_id)
            is_short_by_duration = (isinstance(duration_seconds, int) and duration_seconds < 60) if duration_seconds else False
            
            is_shorts_url = self.shorts_detector.is_shorts_by_url(video_id)
            
            return {
                'last_video_id': video_id,
                'last_video_title': snippet['title'],
                'last_video_published_raw': snippet['publishedAt'],
                'last_video_published': self._format_date(snippet['publishedAt']),
                'last_video_url': f"https://youtube.com/watch?v={video_id}",
                'last_video_is_shorts_url': is_shorts_url,
                'duration_seconds': duration_seconds,
                'last_video_is_short_by_duration': is_short_by_duration
            }
            
        except Exception as e:
            return None
        

        
    def _calculate_shorts_confidence(self, search_info, last_video_info, is_shorts_title, is_shorts_desc):
        """Calcula score de confiança de ser canal de shorts (0-100) - VERSÃO SIMPLIFICADA"""
        score = 0
        
        # Pesos simplificados (sem thumbnail):
        # URL Pattern: 60 pontos (mais confiável)
        # Keywords: 40 pontos
        
        if search_info.get('search_video_is_shorts_url'):
            score += 50
        if search_info.get('search_video_is_shorts_keyword'):
            score += 10
        
        if last_video_info.get('last_video_is_shorts_url'):
            score += 25
        if last_video_info.get('last_video_is_short_by_duration'):
            score += 5
        
        if is_shorts_title:
            score += 5
        if is_shorts_desc:
            score += 5
        
        return min(100, score)











    def _parse_channel_data(self, channel_item, search_shorts_info=None):
        # ✅ GARANTIR que todos os dicts existem
        snippet = channel_item.get('snippet') or {}
        statistics = channel_item.get('statistics') or {}
        branding = channel_item.get('brandingSettings') or {}
        
        # ✅ Extrair valores seguros
        description = snippet.get('description', '')
        title = snippet.get('title', '')
        email = self._extract_email(description)
        
        is_shorts_title = self.shorts_detector.detect_shorts_keywords(title)
        is_shorts_desc = self.shorts_detector.detect_shorts_keywords(description)
        shorts_mentions = self.shorts_detector.count_shorts_mentions(description)
        
        # Info da busca
        if search_shorts_info:
            shorts_from_search = search_shorts_info
        else:
            shorts_from_search = {
                'search_video_is_shorts_url': False,
                'search_video_is_shorts_keyword': False,
                'search_video_shorts_score': 0
            }
        
        # Último vídeo
        last_video_shorts_info = {}
        last_video_data = self._get_last_channel_video_with_shorts(channel_item['id'])
        
        if last_video_data:
            last_video_shorts_info = {
                'last_video_is_shorts_url': last_video_data.get('last_video_is_shorts_url', False),
                'last_video_duration_seconds': last_video_data.get('duration_seconds'),
                'last_video_is_short_by_duration': last_video_data.get('last_video_is_short_by_duration', False)
            }
        





















        # ================================================


        # ========== MAPA DE PAÍSES ==========
        country_code = snippet.get('country', '')
        country_name = self.COUNTRIES_MAP.get(country_code.upper(), country_code)

        # ==========================================


        channel_data = {
            'channel_id': channel_item['id'],
            'channel_title': title,
            
            # URL Pattern
            'search_video_is_shorts_url': shorts_from_search.get('search_video_is_shorts_url', False),
            'last_video_is_shorts_url': last_video_shorts_info.get('last_video_is_shorts_url', False),
            
            # Keywords
            'search_video_is_shorts_keyword': shorts_from_search.get('search_video_is_shorts_keyword', False),
            'is_shorts_channel': is_shorts_title or is_shorts_desc,
            'shorts_in_title': is_shorts_title,
            'shorts_in_description': is_shorts_desc,
            'shorts_mentions_count': shorts_mentions,
            
            # Duração
            'last_video_duration_seconds': last_video_shorts_info.get('last_video_duration_seconds'),
            'last_video_is_short_by_duration': last_video_shorts_info.get('last_video_is_short_by_duration', False),
            
            # Scores
            'search_video_shorts_score': shorts_from_search.get('search_video_shorts_score', 0),
            'shorts_confidence_score': self._calculate_shorts_confidence(
                shorts_from_search, last_video_shorts_info, is_shorts_title, is_shorts_desc
            ),

            # =========================================================

            'custom_url': snippet.get('customUrl', ''),
            'channel_url': f"https://www.youtube.com/channel/{channel_item['id']}",
            
            'description': description[:500],
            'email': email,
            
            # ========== COLUNAS ATUALIZADAS ==========
            'country': country_code,           # Sigla (ex: "BR")
            'country_name': country_name,      # Nome completo (ex: "Brazil")
            # =========================================
            
            'published_at': snippet.get('publishedAt', ''),
            'created_date': self._format_date(snippet.get('publishedAt', '')),
            
            'subscriber_count': self._safe_int(statistics.get('subscriberCount')),
            'view_count': self._safe_int(statistics.get('viewCount')),
            'video_count': self._safe_int(statistics.get('videoCount')),
            'hidden_subscriber_count': statistics.get('hiddenSubscriberCount', False),
            
            'keywords': (branding.get('channel') or {}).get('keywords', ''),
            'profile_image': (snippet.get('thumbnails') or {})
                            .get('high', {})
                            .get('url', ''),
            
            'has_email': bool(email),
            'description_length': len(description),
            'videos_last_6_months': 0,
            'avg_videos_per_month': 0,
            'monthly_videos_detail': '',
            
            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        
            **self._extract_links(description), 
        }

        # Último vídeo
        last_video_data = self._get_last_channel_video_optimized(channel_item['id']) 
        if last_video_data:
            channel_data.update(last_video_data)
        
        # ========== Playlists ==========
        playlist_names, playlist_counts = self.get_channel_playlists(channel_item['id'], max_playlists=10)
        channel_data['playlist_names'] = playlist_names
        channel_data['playlist_video_counts'] = playlist_counts
        channel_data['playlist_count'] = len(playlist_names.split('; ')) if playlist_names else 0
        # ==============================
        
        # ========== Métricas derivadas (APENAS UMA VEZ) ==========
        derived = self._calculate_derived_metrics(channel_data)
        channel_data.update(derived)
        # =========================================================

        return channel_data






    def _calculate_content_score(self, description, title):
        """Calcula score de qualidade do conteúdo (0-100)"""
        score = 50  # Base
        
        # Pontos POSITIVOS (conteúdo de qualidade)
        quality_keywords = {
            'tutorial': 10, 'education': 10, 'course': 15, 'learn': 8,
            'how to': 12, 'guide': 10, 'training': 10, 'academy': 15,
            'masterclass': 20, 'workshop': 12, 'professional': 10,
            'business': 10, 'enterprise': 12, 'company': 8,
            'educational': 10, 'knowledge': 8, 'teaching': 10,
            'instruction': 8, 'expert': 10, 'specialist': 10
        }
        
        for keyword, points in quality_keywords.items():
            if keyword in description or keyword in title:
                score += points
        
        # Pontos NEGATIVOS (conteúdo casual/Shorts)
        casual_keywords = {
            'shorts': -25, '#shorts': -30, '#short': -25, 'short': -20,
            'tiktok': -20, 'reels': -20, 'funny': -15, 'compilation': -20,
            'memes': -20, 'fails': -15, 'prank': -15, 'challenge': -10,
            'viral': -15, 'trending': -10, 'react': -10, 'reaction': -10,
            'entertainment': -5, 'fun': -5, 'laugh': -5, 'comedy': -5,
            '秒': -25, '短編': -25, '短視頻': -25  # Palavras em chinês/japonês para shorts
        }
        
        for keyword, points in casual_keywords.items():
            if keyword in description or keyword in title:
                score += points
        
        # Limitar entre 0-100
        return max(0, min(100, score))





    def _get_last_channel_video_optimized(self, channel_id):
        """Obtém último upload com CACHE"""
        
        # PRIMEIRO verificar no cache via data_handler
        # (precisa passar data_handler para o YouTubeAPI ou fazer diferente)
        
        try:
            # Busca normal se não tiver cache
            activities_response = self.youtube.activities().list(
                channelId=channel_id,
                part='snippet,contentDetails',
                maxResults=1
            ).execute()
            
            self.quota_used += 1
            
            if activities_response.get('items'):
                item = activities_response['items'][0]
                if item['snippet']['type'] == 'upload':
                    video_id = item['contentDetails']['upload']['videoId']
                    return {
                        'last_video_id': video_id,
                        'last_video_title': item['snippet']['title'],
                        'last_video_published_raw': item['snippet']['publishedAt'],
                        'last_video_published': self._format_date(item['snippet']['publishedAt']),
                        'last_video_url': f"https://youtube.com/watch?v={video_id}"
                    }
        except Exception as e:
            pass
        return {}
    
    def _extract_links(self, text):
        """Extrai links sociais e websites da descrição"""
        # Mantenha o código original aqui
        if not text:
            return {}
        
        links = {'websites': [], 'social_media': {}}
        patterns = {
            'instagram': r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([a-zA-Z0-9._]+)',
            'twitter': r'(?:https?:\/\/)?(?:www\.)?(?:twitter|x)\.com\/([a-zA-Z0-9_]+)',
            'facebook': r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/([a-zA-Z0-9.]+)',
            'tiktok': r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([a-zA-Z0-9._]+)',
            'linkedin': r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|company)\/([a-zA-Z0-9-]+)',
            'website': r'(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:\/[^\s]*)?'
        }
        
        for platform, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and platform != 'website':
                links['social_media'][platform] = list(set(matches))[:3]
        
        website_matches = re.findall(patterns['website'], text, re.IGNORECASE)
        unique_websites = []
        seen = set()
        
        for site in website_matches:
            if not any(social in site.lower() for social in ['youtube', 'instagram', 'twitter', 'facebook', 'tiktok', 'linkedin']):
                domain = site.lower()
                if domain not in seen:
                    seen.add(domain)
                    unique_websites.append(f"https://{domain}")
        
        links['websites'] = unique_websites[:5]
        
        return {
            'social_links': '; '.join([f"{k}:{','.join(v)}" for k, v in links['social_media'].items()]),
            'websites': '; '.join(links['websites']),
            'total_links_found': len(links['social_media']) + len(links['websites'])
        }

    def _extract_email(self, text):
        """Extrai e-mail do texto usando regex"""
        # Mantenha o código original aqui
        if not text:
            return ""
        
        email_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9._%+-]+\[at\][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text)
            if matches:
                email = matches[0].replace('[at]', '@').replace(' ', '')
                if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    return email
        
        return ""
    








    
    def _calculate_derived_metrics(self, channel_data):
        """Calcula métricas derivadas dos dados do canal - VERSÃO CORRIGIDA"""
        metrics = {}
        
        # 1. Dias desde último vídeo - CORREÇÃO TIMEZONE
        if channel_data.get('last_video_published_raw'):
            try:
                raw_date = channel_data['last_video_published_raw']
                last_video_date = parser.isoparse(raw_date)
                
                # Converter para timezone UTC se tiver timezone
                if last_video_date.tzinfo is not None:
                    last_video_utc = last_video_date.astimezone(timezone.utc)
                    now_utc = datetime.now(timezone.utc)
                    days_since = (now_utc - last_video_utc).days
                else:
                    # Se não tem timezone, usar datetime.now() normal
                    days_since = (datetime.now() - last_video_date).days
                
                metrics['days_since_last_video'] = days_since
                
            except Exception as e:
                metrics['days_since_last_video'] = -1
        else:
            metrics['days_since_last_video'] = -1









        # 2. Densidade de e-mail
        description = channel_data.get('description', '')
        email = channel_data.get('email', '')
        # Mantenha a lógica original de densidade, mas desconsidere avg_videos_per_month
        metrics['email_density'] = 0 # Implementação simplificada
        
        # 3. Score de atividade (0-100) - AJUSTADO para depender SÓ de recência/email
        activity_score = 0
        
        days_since = metrics.get('days_since_last_video', 999)
        
        # Recência do último vídeo (pesos ajustados)
        if days_since <= 7:
            activity_score += 45
        elif days_since <= 30:
            activity_score += 30
        elif days_since <= 90:
            activity_score += 15
        
        # Canal tem e-mail (peso ajustado)
        if channel_data.get('email'):
            activity_score += 20 # Sobe para 20
        
        # Para forçar o score a ser significativo
        if activity_score > 0 and channel_data.get('subscriber_count', 0) > 1000:
            activity_score += 15
        
        metrics['activity_score'] = min(100, activity_score)
        
        # 4. Classificação por tamanho
        subs = channel_data.get('subscriber_count', 0)
        if subs >= 1000000:
            metrics['channel_size'] = 'Mega'
        elif subs >= 100000:
            metrics['channel_size'] = 'Large'
        elif subs >= 10000:
            metrics['channel_size'] = 'Medium'
        elif subs >= 1000:
            metrics['channel_size'] = 'Small'
        else:
            metrics['channel_size'] = 'Micro'





        
        return metrics

    def _safe_int(self, value, default=0):
        """Converte para int com tratamento seguro"""
        try:
            return int(value) if value else default
        except:
            return default
    
    def _format_date(self, date_string):
        """Formata data ISO do YouTube para formato legível"""
        if not date_string:
            return ""
        
        try:
            if '.' in date_string:
                date_string = date_string.split('.')[0] + 'Z'
            
            dt = parser.isoparse(date_string)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_string
    
    def get_quota_used(self):
        """Retorna quota utilizada"""
        return self.quota_used