class AIRecommendationEngine:
    """Core AI engine for music recommendations"""
    
    def __init__(self, database: MusicDatabase):
        self.db = database
        self.songs_df = None
        self.tfidf_matrix = None
        self.feature_matrix = None
        self.scaler = StandardScaler()
        self.load_data()
    
    def load_data(self):
        """Load and preprocess music data"""
        self.songs_df = self.db.get_all_songs()
        if len(self.songs_df) == 0:
            return
        
        # Create text features for content-based filtering
        self.songs_df['text_features'] = (
            self.songs_df['genre'] + ' ' + 
            self.songs_df['artist'] + ' ' + 
            self.songs_df['year'].astype(str)
        )
        
        # TF-IDF for text features
        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        self.tfidf_matrix = tfidf.fit_transform(self.songs_df['text_features'])
        
        # Numerical features for audio characteristics
        audio_features = ['energy', 'danceability', 'valence', 'acousticness', 'popularity']
        feature_data = self.songs_df[audio_features].fillna(0)
        self.feature_matrix = self.scaler.fit_transform(feature_data)
    
    def get_content_based_recommendations(self, song_id: int, n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations based on song content similarity"""
        if self.songs_df is None or len(self.songs_df) == 0:
            return []
        
        # Find the song index
        song_idx = self.songs_df[self.songs_df['id'] == song_id].index
        if len(song_idx) == 0:
            return []
        
        song_idx = song_idx[0]
        
        # Calculate similarities
        text_sim = cosine_similarity(self.tfidf_matrix[song_idx:song_idx+1], self.tfidf_matrix).flatten()
        audio_sim = cosine_similarity(self.feature_matrix[song_idx:song_idx+1], self.feature_matrix).flatten()
        
        # Combine similarities (weighted)
        combined_sim = 0.3 * text_sim + 0.7 * audio_sim
        
        # Get top similar songs (excluding the input song)
        similar_indices = combined_sim.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            song = self.songs_df.iloc[idx]
            recommendations.append({
                'id': int(song['id']),
                'title': song['title'],
                'artist': song['artist'],
                'genre': song['genre'],
                'year': int(song['year']),
                'similarity_score': float(combined_sim[idx])
            })
        
        return recommendations
    
    def get_genre_based_recommendations(self, preferred_genres: List[str], n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations based on preferred genres"""
        if self.songs_df is None or len(self.songs_df) == 0:
            return []
        
        # Filter songs by preferred genres
        genre_mask = self.songs_df['genre'].isin(preferred_genres)
        genre_songs = self.songs_df[genre_mask]
        
        if len(genre_songs) == 0:
            # Fallback to popular songs
            genre_songs = self.songs_df.nlargest(n_recommendations, 'popularity')
        
        # Sort by popularity and get top recommendations
        recommendations = []
        for _, song in genre_songs.nlargest(n_recommendations, 'popularity').iterrows():
            recommendations.append({
                'id': int(song['id']),
                'title': song['title'],
                'artist': song['artist'],
                'genre': song['genre'],
                'year': int(song['year']),
                'popularity': int(song['popularity'])
            })
        
        return recommendations
    
    def get_hybrid_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """Get hybrid recommendations combining multiple approaches"""
        user_ratings = self.db.get_user_ratings(user_id)
        
        if len(user_ratings) == 0:
            # New user - recommend popular songs
            return self.get_popular_recommendations(n_recommendations)
        
        # Get user's favorite songs (rating >= 4)
        favorite_songs = user_ratings[user_ratings['rating'] >= 4]
        
        if len(favorite_songs) == 0:
            return self.get_popular_recommendations(n_recommendations)
        
        # Get content-based recommendations for each favorite song
        all_recommendations = []
        for _, song in favorite_songs.iterrows():
            recs = self.get_content_based_recommendations(song['song_id'], 3)
            all_recommendations.extend(recs)
        
        # Remove duplicates and already rated songs
        rated_song_ids = set(user_ratings['song_id'].values)
        unique_recs = []
        seen_ids = set()
        
        for rec in all_recommendations:
            if rec['id'] not in seen_ids and rec['id'] not in rated_song_ids:
                unique_recs.append(rec)
                seen_ids.add(rec['id'])
        
        # Sort by similarity score and return top N
        unique_recs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return unique_recs[:n_recommendations]
    
    def get_popular_recommendations(self, n_recommendations: int = 5) -> List[Dict]:
        """Get popular song recommendations"""
        if self.songs_df is None or len(self.songs_df) == 0:
            return []
        
        popular_songs = self.songs_df.nlargest(n_recommendations, 'popularity')
        recommendations = []
        
        for _, song in popular_songs.iterrows():
            recommendations.append({
                'id': int(song['id']),
                'title': song['title'],
                'artist': song['artist'],
                'genre': song['genre'],
                'year': int(song['year']),
                'popularity': int(song['popularity'])
            })
        
        return recommendations