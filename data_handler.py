from datetime import datetime, timedelta
import pandas as pd
import json
import os
from datetime import datetime
import sys
import traceback

class DataHandler:









    def __init__(self, export_path):
        self.output_dir = export_path
        
        # Usar caminho da pasta config se existir (SEGURO - não cria nada)
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        if os.path.exists(config_dir) and os.path.isdir(config_dir):
            self.history_file = os.path.join(config_dir, 'crawl_history.json')
        else:
            # Fallback: usar raiz do projeto se config não existir
            self.history_file = 'crawl_history.json'
        
        self.master_file = os.path.join(export_path, 'MASTER', 'youtube_channels_master.csv')
        
        # Criar pasta MASTER se não existir
        master_dir = os.path.join(export_path, 'MASTER')
        if not os.path.exists(master_dir):
            os.makedirs(master_dir)


        # 1. Migrar formato antigo para novo se necessário
        self._migrate_old_format()
        
        # 2. Criar arquivo se não existir
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump({
                    'created': datetime.now().isoformat(),
                    'last_cleanup': datetime.now().isoformat(),
                    'sessions': []
                }, f, indent=2)
        
        # 3. Limpar sessões antigas
        self.cleanup_old_sessions(30)

        # ========== VERIFICAR SE DEVE RODAR AUTO-CLEANUP ==========
        if self.should_run_auto_cleanup():
            # ↓↓↓ CORREÇÃO: cleanup_old_sessions (não cleanup_old_sessions_only) ↓↓↓
            self.cleanup_old_sessions(30)  # ← NOME CORRETO
        else:
            print("Auto-cleanup está desativado nas configurações")

    def should_run_auto_cleanup(self):
        """Verifica se auto-cleanup está habilitado"""
        try:
            # Caminho para o arquivo de configuração
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', 'config', 'cleanup_settings.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get('auto_cleanup_enabled', True)
            
            return True  # Padrão se arquivo não existe
            
        except Exception as e:
            print(f"Erro ao verificar auto-cleanup: {e}")
            return True  # Padrão se erro










    def _migrate_old_format(self):
        """Converte formato antigo (lista) para novo (dicionário)"""
        if not os.path.exists(self.history_file):
            return
        
        try:
            with open(self.history_file, 'r') as f:
                content = f.read().strip()
                
            if not content:
                return
                
            data = json.loads(content)
            
            # Se for lista (formato antigo), converter
            if isinstance(data, list):
                print("🔄 Migrando histórico do formato antigo para novo...")
                
                new_data = {
                    'created': datetime.now().isoformat(),
                    'last_cleanup': datetime.now().isoformat(),
                    'sessions': data
                }
                
                with open(self.history_file, 'w') as f:
                    json.dump(new_data, f, indent=2)
                
                print(f"Migração concluída: {len(data)} sessões migradas")
                
        except Exception as e:
            print(f"Erro na migração do histórico: {e}")


    def save_history(self, entry):
        """Salva um resumo da execução no histórico JSON."""
        try:
            with open(self.history_file, 'r+') as f:
                try:
                    data = json.load(f)
                    sessions = data.get('sessions', [])
                except json.JSONDecodeError:
                    data = {
                        'created': datetime.now().isoformat(),
                        'last_cleanup': datetime.now().isoformat(),
                        'sessions': []
                    }
                    sessions = []
                
                # Garante que entry é serializável
                if 'data_preview' in entry:
                    entry['data_preview'] = entry['data_preview'][:5]
                
                sessions.append(entry)
                data['sessions'] = sessions
                
                f.seek(0)
                json.dump(data, f, indent=2)
                
            # Verificar expiração automática
            self.auto_cleanup()
            
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")







    def load_cleanup_setting(self):
        """Carrega configuração de auto-cleanup"""
        try:
            # Caminho para o arquivo de configuração
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config', 'cleanup_settings.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get('auto_cleanup_enabled', True)
            
            return True  # Padrão se arquivo não existe
            
        except Exception as e:
            print(f"Erro ao carregar configuração de cleanup: {e}")
            return True  # Padrão se erro












    def auto_cleanup(self, max_age_days=30, force=False):
        """Remove automaticamente sessões antigas se configurado"""
        
        # Verificar se auto-cleanup está habilitado
        if not force:
            # Aqui você precisa ler a configuração salva
            # Pode passar como parâmetro ou ler de arquivo
            cleanup_enabled = self.load_cleanup_setting()  # Você precisa implementar
            if not cleanup_enabled:
                return False, "Auto-cleanup disabled by user"
        
        try:
            if not os.path.exists(self.history_file):
                return
            
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            sessions = data.get('sessions', [])
            if not sessions:
                return
            
            # Verificar última limpeza
            last_cleanup_str = data.get('last_cleanup', '')
            if last_cleanup_str:
                last_cleanup = datetime.fromisoformat(last_cleanup_str)
                # Só limpar a cada 7 dias para performance
                if (datetime.now() - last_cleanup).days < 7:
                    return
            
            # Filtrar sessões antigas
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            kept_sessions = []
            removed_count = 0
            
            for session in sessions:
                session_date_str = session.get('timestamp', '')
                if session_date_str:
                    try:
                        session_date = datetime.fromisoformat(session_date_str)
                        if session_date >= cutoff_date:
                            kept_sessions.append(session)
                        else:
                            removed_count += 1
                    except:
                        kept_sessions.append(session)
                else:
                    kept_sessions.append(session)
            
            # Atualizar se houve remoções
            if removed_count > 0:
                data['sessions'] = kept_sessions
                data['last_cleanup'] = datetime.now().isoformat()
                
                with open(self.history_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"🧹 Limpeza automática: {removed_count} sessões antigas removidas")
                
        except Exception as e:
            print(f"Erro na limpeza automática: {e}")













    def cleanup_old_sessions(self, max_age_days=30):
        """Remove apenas sessões antigas, mantendo as recentes"""
        try:
            if not os.path.exists(self.history_file):
                return False, "No history file found"
            
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            sessions = data.get('sessions', [])
            if not sessions:
                return False, "No sessions to clean"
            
            # Filtrar sessões antigas
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            kept_sessions = []
            removed_sessions = []
            
            for session in sessions:
                session_date_str = session.get('timestamp', '')
                if session_date_str:
                    try:
                        session_date = datetime.fromisoformat(session_date_str)
                        if session_date >= cutoff_date:
                            kept_sessions.append(session)
                        else:
                            removed_sessions.append(session)
                    except:
                        kept_sessions.append(session)
                else:
                    kept_sessions.append(session)
            
            if not removed_sessions:
                return False, "No old sessions to remove"
            
            # Atualizar arquivo
            data['sessions'] = kept_sessions
            data['last_cleanup'] = datetime.now().isoformat()
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True, f"Removed {len(removed_sessions)} old sessions (kept {len(kept_sessions)})"
            
        except Exception as e:
            return False, f"Error cleaning old sessions: {str(e)}"




    def export_channels(self, channels_data, filename_prefix, file_format):
        
        """Exporta para arquivo individual E atualiza a planilha mestra"""
        # 1. Exportação normal (individual)
        individual_path = self._export_individual(channels_data, filename_prefix, file_format)
        
        # 2. Atualizar planilha mestra com o nome do arquivo individual
        if individual_path:
            # Extrair apenas o nome do arquivo sem extensão
            source_name = os.path.splitext(os.path.basename(individual_path))[0]
            self._update_master_file(channels_data, source_name)
        
        return individual_path





    def _export_individual(self, channels_data, filename_prefix, file_format):
            """
            Exporta os dados, usando self.output_dir (caminho mestre)
            """
            if not channels_data:
                print("Nenhum dado para exportar.")
                return None

            try:
                df = pd.DataFrame(channels_data)
                
                preferred_order = [
                    'channel_id', 'channel_title', 'custom_url', 
                    'subscriber_count', 'view_count', 'video_count', 
                    'country', 'country_name',
                    
                    # ========== COLUNAS DE DETECÇÃO DE SHORTS (SIMPLIFICADAS) ==========
                    # Método URL Pattern
                    'search_video_is_shorts_url',
                    'last_video_is_shorts_url',
                    
                    # Método Keywords
                    'is_shorts_channel',
                    'shorts_in_title',
                    'shorts_in_description', 
                    'shorts_mentions_count',
                    'search_video_is_shorts_keyword',
                    
                    # Método Duração
                    'last_video_duration_seconds',
                    'last_video_is_short_by_duration',
                    
                    # Scores
                    'search_video_shorts_score',
                    'shorts_confidence_score',
                    
                    # Score de conteúdo (existente)
                    'content_warning_score',
                    # ===================================================
                    
                    'has_email', 'email',
                    'playlist_count', 'playlist_names', 'playlist_video_counts',
                    'description', 'published_at',
                    'last_video_title', 'last_video_published', 'days_since_last_video',
                    'activity_score', 'activity_status', 'channel_size',
                    'social_links', 'websites', 'total_links_found',
                    'keywords', 'profile_image', 'collected_at'
                ]




                existing_columns = [col for col in preferred_order if col in df.columns]
                remaining_columns = [col for col in df.columns if col not in existing_columns]
                df = df[existing_columns + remaining_columns]

                # --- USO DO CAMINHO MESTRE ---
                # output_dir é definido no __init__ do DataHandler e vem do main.py
                output_dir = self.output_dir 
                clean_filename = os.path.splitext(filename_prefix)[0]

                # Garante que o diretório de exportação existe
                if not os.path.exists(output_dir):
                    print(f"DEBUG: Criando pasta de exportação: {output_dir}")
                    os.makedirs(output_dir)

                # (Restante da lógica de exportação...)
                normalized_format = file_format.lower().replace('excel', 'xlsx')
                
                if normalized_format == 'csv':
                    file_extension = 'csv'
                    full_path = os.path.join(output_dir, f"{clean_filename}.{file_extension}")
                    df.to_csv(full_path, index=False, encoding='utf-8-sig', sep=';')
                
                elif normalized_format == 'xlsx':
                    file_extension = 'xlsx'
                    full_path = os.path.join(output_dir, f"{clean_filename}.{file_extension}")
                    
                    # Uso explícito do ExcelWriter com openpyxl
                    writer = pd.ExcelWriter(full_path, engine='openpyxl')
                    df.to_excel(writer, index=False, sheet_name='YouTube Channels')
                    writer.close() # Garante que o arquivo é finalizado.
                
                else:
                    print(f"ERRO CRÍTICO NA EXPORTAÇÃO: Formato de arquivo '{file_format}' não suportado.")
                    return None
                
                return full_path

            except Exception as e:
                # Bloco de debug de traceback mantido
                print("\n" + "="*50)
                print(f"ERRO CRÍTICO NA EXPORTAÇÃO (TRACEBACK COMPLETO) para {filename_prefix}:")
                traceback.print_exc(file=sys.stdout) # Força a saída para o console
                sys.stdout.flush()
                print("="*50 + "\n")
                return None





    def _ensure_column_order(self, df):
        """Garante que as colunas de filtro estão na ordem correta"""
        
        # Ordem preferida (a mesma que você já tem)
        preferred_order = [
            'channel_id', 'channel_title', 'custom_url', 
            'subscriber_count', 'view_count', 'video_count', 
            'country', 'country_name',
            
            # ========== COLUNAS DE FILTRO ==========
            'is_shorts_channel',
            'content_warning_score',
            'shorts_in_title',
            'shorts_in_description',
            'shorts_mentions_count',
            # ======================================
            
            'has_email', 'email',
            'playlist_count', 'playlist_names', 'playlist_video_counts',
            'description', 'published_at',
            'last_video_title', 'last_video_published', 'days_since_last_video',
            'activity_score', 'channel_size',  # Removi 'activity_status' se não existe
            'social_links', 'websites', 'total_links_found',
            'keywords', 'profile_image', 'collected_at',
            
            # Colunas da mestra
            'added_to_master', 'source_file', 'master_update_count'
        ]
        
        # Garantir que todas as colunas da preferred_order existam
        for col in preferred_order:
            if col not in df.columns:
                df[col] = None
        
        # Separar colunas que existem
        existing_columns = [col for col in preferred_order if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in existing_columns]
        
        # Ordenar
        if existing_columns:
            df = df[existing_columns + remaining_columns]
        
        return df

















    def _update_master_file(self, channels_data, source_filename):
        """Atualiza planilha mestra com controle de versões"""
        try:
            if not channels_data:
                return
            
            df_new = pd.DataFrame(channels_data)
            
            # Colunas de metadados da mestra
            df_new['added_to_master'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df_new['source_file'] = source_filename
            df_new['master_update_count'] = 1  # Primeira inclusão
            
            # Se arquivo mestre não existe, criar
            if not os.path.exists(self.master_file):
                # ✅ FORÇAR ORDEM CORRETA desde o início
                df_new = self._ensure_column_order(df_new)
                df_new.to_csv(self.master_file, index=False, encoding='utf-8-sig', sep=';')
                return
            
            # Ler mestra existente e REMOVER colunas Unnamed
            df_master = pd.read_csv(self.master_file, sep=';', encoding='utf-8-sig')
            
            # ✅ REMOVER COLUNAS Unnamed
            unnamed_cols = [col for col in df_master.columns if 'Unnamed' in str(col)]
            if unnamed_cols:
                print(f"⚠️ Removendo colunas Unnamed da mestra: {unnamed_cols}")
                df_master = df_master.drop(columns=unnamed_cols)
            
            # Identificar canais existentes e novos
            existing_ids = set(df_master['channel_id'].astype(str))
            new_mask = ~df_new['channel_id'].astype(str).isin(existing_ids)
            update_mask = df_new['channel_id'].astype(str).isin(existing_ids)
            
            # Novos canais
            new_channels = df_new[new_mask]
            
            # Canais existentes (atualizar dados se necessário)
            if update_mask.any():
                updated_channels = df_new[update_mask]
                # Remover versões antigas destes canais da mestra
                df_master = df_master[~df_master['channel_id'].astype(str).isin(
                    updated_channels['channel_id'].astype(str)
                )]
                # Incrementar contador de atualizações
                if 'master_update_count' in updated_channels.columns:
                    updated_channels.loc[:, 'master_update_count'] = updated_channels['master_update_count'] + 1
                else:
                    updated_channels['master_update_count'] = 2
            
            # ✅ GARANTIR que todos os DataFrames têm as mesmas colunas
            new_channels = self._ensure_column_order(new_channels)
            if 'updated_channels' in locals():
                updated_channels = self._ensure_column_order(updated_channels)
            
            # Combinar tudo
            if 'updated_channels' in locals():
                df_updated = pd.concat([df_master, new_channels, updated_channels], ignore_index=True)
            else:
                df_updated = pd.concat([df_master, new_channels], ignore_index=True)
            
            # ✅ Remover possíveis duplicatas de colunas
            df_updated = df_updated.loc[:, ~df_updated.columns.duplicated()]
            
            # Salvar
            df_updated.to_csv(self.master_file, index=False, encoding='utf-8-sig', sep=';')
            
            print(f"✅ Mestra: +{len(new_channels)} novos, ↑{len(updated_channels) if 'updated_channels' in locals() else 0} atualizados")
            
        except Exception as e:
            print(f"❌ Erro mestra: {e}")
            import traceback
            traceback.print_exc()












    def clean_master_duplicates(self):
        """Remove duplicatas da planilha mestra (por segurança)"""
        try:
            if not os.path.exists(self.master_file):
                return False, "Master file doesn't exist"
            
            df = pd.read_csv(self.master_file, sep=';', encoding='utf-8-sig')
            
            # Remover duplicatas mantendo a entrada mais recente
            before = len(df)
            df = df.drop_duplicates(subset=['channel_id'], keep='last')
            after = len(df)
            
            if before > after:
                df.to_csv(self.master_file, index=False, encoding='utf-8-sig', sep=';')
                return True, f"Removed {before - after} duplicates from master"
            
            return True, "No duplicates found in master"
            
        except Exception as e:
            return False, f"Error cleaning master: {str(e)}"



    def clear_history(self):
        """Limpa todo o histórico de crawlers"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
                # Recria o arquivo vazio
                with open(self.history_file, 'w') as f:
                    json.dump([], f)
                return True, "Histórico de crawlers limpo com sucesso"
            return False, "Nenhum histórico encontrado"
        except Exception as e:
            return False, f"Erro ao limpar histórico: {str(e)}"

    def clear_cache(self):
        """
        Limpa o cache de IDs de canais já crawleados.
        Na sua implementação, o cache está no próprio arquivo de histórico,
        então isso é equivalente a limpar o histórico.
        """
        try:
            # Na sua implementação, os IDs vêm do histórico
            # Para limpar o cache, recriamos o histórico vazio
            if os.path.exists(self.history_file):
                with open(self.history_file, 'w') as f:
                    json.dump([], f)
                return True, "Cache de canais limpo com sucesso"
            return False, "Nenhum cache encontrado"
        except Exception as e:
            return False, f"Erro ao limpar cache: {str(e)}"
        




    # No data_handler.py
    def get_last_video_from_cache(self, channel_id):
        """Tenta obter último vídeo do cache/histórico"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                # Do mais recente para o mais antigo
                for session in reversed(history):
                    if 'data_preview' in session:
                        for channel in session['data_preview']:
                            if channel.get('channel_id') == channel_id:
                                # Retornar dados do último vídeo se existirem
                                last_video_data = {}
                                for key in ['last_video_id', 'last_video_title', 
                                        'last_video_published_raw', 'last_video_published',
                                        'last_video_url', 'days_since_last_video']:
                                    if key in channel:
                                        last_video_data[key] = channel[key]
                                return last_video_data if last_video_data else None
        return None













    def get_cached_channel_data(self, channel_ids):
        """
        Retorna dados cacheados do histórico para os IDs fornecidos.
        Retorna: (cached_data, uncached_ids)
        """
        cached_data = []
        uncached_ids = []
        
        if not os.path.exists(self.history_file):
            return [], channel_ids
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            # Converter para dicionário rápido: channel_id -> channel_data
            cache_dict = {}
            
            # Percorrer histórico do MAIS RECENTE ao MAIS ANTIGO
            for session in reversed(history):
                if 'data_preview' in session:
                    for channel in session['data_preview']:
                        cid = channel.get('channel_id')
                        if cid and cid not in cache_dict:
                            cache_dict[cid] = channel
            
            # Separar IDs cacheados e não cacheados
            for channel_id in channel_ids:
                if channel_id in cache_dict:
                    cached_data.append(cache_dict[channel_id])
                else:
                    uncached_ids.append(channel_id)
                    
        except Exception as e:
            print(f"Error reading cache from history: {e}")
            uncached_ids = channel_ids
        
        return cached_data, uncached_ids






    def get_history_stats(self):
        """Retorna estatísticas do histórico com informações de expiração"""
        stats = {
            'history_exists': False,
            'session_count': 0,
            'cache_count': 0,
            'oldest_session': None,
            'auto_cleanup_enabled': True,
            'cleanup_days': 30,
            'sessions_to_expire': 0
        }
        
        if not os.path.exists(self.history_file):
            return stats
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                stats['history_exists'] = True
                
                sessions = data.get('sessions', [])
                stats['session_count'] = len(sessions)
                
                # Contar IDs em cache
                all_ids = set()
                oldest_date = None
                
                for entry in sessions:
                    # Data da sessão
                    session_date_str = entry.get('timestamp', '')
                    if session_date_str:
                        try:
                            session_date = datetime.fromisoformat(session_date_str)
                            if oldest_date is None or session_date < oldest_date:
                                oldest_date = session_date
                        except:
                            pass
                    
                    # IDs de canais
                    if 'data_preview' in entry:
                        for channel in entry['data_preview']:
                            if 'channel_id' in channel:
                                all_ids.add(channel['channel_id'])
                
                stats['cache_count'] = len(all_ids)
                
                # Calcular sessões que expirariam
                if oldest_date:
                    stats['oldest_session'] = oldest_date.strftime('%Y-%m-%d')
                    days_old = (datetime.now() - oldest_date).days
                    stats['days_oldest'] = days_old
                    stats['sessions_to_expire'] = max(0, days_old - 30)
                    
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
        
        return stats




    def load_all_crawled_ids(self):
        """Carrega todos os IDs já processados para evitar duplicatas."""
        crawled_ids = set()
        
        if not os.path.exists(self.history_file):
            return crawled_ids
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                sessions = data.get('sessions', [])
                
                for entry in sessions:
                    if 'data_preview' in entry:
                        for channel in entry['data_preview']:
                            if 'channel_id' in channel:
                                crawled_ids.add(channel['channel_id'])
        except Exception:
            return set()
        
        return crawled_ids