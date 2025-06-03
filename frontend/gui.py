import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from backend.database import MusicDatabase
from backend.ai_engine import AIRecommendationEngine

class MusicRecommendationGUI:
    """GUI interface for the music recommendation system"""
    
    def __init__(self):
        self.db = MusicDatabase()
        self.ai_engine = AIRecommendationEngine(self.db)
        self.current_user = "default_user"
        
        self.root = tk.Tk()
        self.root.title("AI Music Recommendation System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2C3E50')
        
        self.setup_gui()
        self.load_songs()
    
    def setup_gui(self):
        """Setup the GUI components"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#2C3E50')
        style.configure('TLabel', background='#2C3E50', foreground='white', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 AI Music Recommendation System", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Song library
        library_frame = ttk.LabelFrame(main_frame, text="Music Library", padding="10")
        library_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(0, 10))
        
        # Song listbox
        self.song_listbox = tk.Listbox(library_frame, height=15, width=40)
        self.song_listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        scrollbar1 = ttk.Scrollbar(library_frame, orient="vertical")
        scrollbar1.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.song_listbox.config(yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.song_listbox.yview)
        
        # Rating section
        rating_frame = ttk.Frame(library_frame)
        rating_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Label(rating_frame, text="Rate Song:").grid(row=0, column=0, padx=(0, 5))
        self.rating_var = tk.StringVar(value="5")
        rating_combo = ttk.Combobox(rating_frame, textvariable=self.rating_var, 
                                   values=["1", "2", "3", "4", "5"], width=5)
        rating_combo.grid(row=0, column=1, padx=(0, 5))
        
        rate_btn = ttk.Button(rating_frame, text="Rate", command=self.rate_song)
        rate_btn.grid(row=0, column=2)
        
        # Middle panel - Recommendation controls
        control_frame = ttk.LabelFrame(main_frame, text="Get Recommendations", padding="10")
        control_frame.grid(row=1, column=1, sticky=(tk.N, tk.E, tk.W), padx=5)
        
        # Similar songs button
        similar_btn = ttk.Button(control_frame, text="Similar to Selected Song", 
                               command=self.get_similar_recommendations)
        similar_btn.grid(row=0, column=0, pady=5, sticky=(tk.E, tk.W))
        
        # Genre-based recommendations
        ttk.Label(control_frame, text="Preferred Genres:").grid(row=1, column=0, pady=(10, 5))
        self.genre_var = tk.StringVar()
        genre_combo = ttk.Combobox(control_frame, textvariable=self.genre_var,
                                  values=["Rock", "Pop", "Electronic", "Alternative", "Grunge", 
                                         "Britpop", "Synthpop", "Funk", "Soul", "Indie Pop"])
        genre_combo.grid(row=2, column=0, pady=5, sticky=(tk.E, tk.W))
        
        genre_btn = ttk.Button(control_frame, text="Recommend by Genre", 
                              command=self.get_genre_recommendations)
        genre_btn.grid(row=3, column=0, pady=5, sticky=(tk.E, tk.W))
        
        # Personal recommendations
        personal_btn = ttk.Button(control_frame, text="Personal Recommendations", 
                                command=self.get_personal_recommendations)
        personal_btn.grid(row=4, column=0, pady=(10, 5), sticky=(tk.E, tk.W))
        
        # Popular songs
        popular_btn = ttk.Button(control_frame, text="Popular Songs", 
                               command=self.get_popular_recommendations)
        popular_btn.grid(row=5, column=0, pady=5, sticky=(tk.E, tk.W))
        
        # Right panel - Recommendations
        rec_frame = ttk.LabelFrame(main_frame, text="Recommendations", padding="10")
        rec_frame.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(10, 0))
        
        self.rec_text = scrolledtext.ScrolledText(rec_frame, height=20, width=50)
        self.rec_text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(1, weight=1)
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
        rec_frame.columnconfigure(0, weight=1)
        rec_frame.rowconfigure(0, weight=1)
    
    def load_songs(self):
        """Load songs into the listbox"""
        songs_df = self.db.get_all_songs()
        self.song_listbox.delete(0, tk.END)
        
        for _, song in songs_df.iterrows():
            display_text = f"{song['title']} - {song['artist']} ({song['genre']}, {song['year']})"
            self.song_listbox.insert(tk.END, display_text)
    
    def get_selected_song_id(self):
        """Get the ID of the currently selected song"""
        selection = self.song_listbox.curselection()
        if not selection:
            return None
        
        songs_df = self.db.get_all_songs()
        return songs_df.iloc[selection[0]]['id']
    
    def rate_song(self):
        """Rate the selected song"""
        song_id = self.get_selected_song_id()
        if song_id is None:
            messagebox.showwarning("No Selection", "Please select a song to rate.")
            return
        
        rating = int(self.rating_var.get())
        self.db.add_rating(self.current_user, song_id, rating)
        messagebox.showinfo("Success", f"Song rated {rating} stars!")
    
    def display_recommendations(self, recommendations: List[Dict], title: str):
        """Display recommendations in the text area"""
        self.rec_text.delete(1.0, tk.END)
        self.rec_text.insert(tk.END, f"=== {title} ===\n\n")
        
        if not recommendations:
            self.rec_text.insert(tk.END, "No recommendations found.")
            return
        
        for i, rec in enumerate(recommendations, 1):
            text = f"{i}. {rec['title']} - {rec['artist']}\n"
            text += f"   Genre: {rec['genre']} | Year: {rec['year']}\n"
            
            if 'similarity_score' in rec:
                text += f"   Similarity: {rec['similarity_score']:.3f}\n"
            elif 'popularity' in rec:
                text += f"   Popularity: {rec['popularity']}/100\n"
            
            text += "\n"
            self.rec_text.insert(tk.END, text)
    
    def get_similar_recommendations(self):
        """Get recommendations similar to selected song"""
        song_id = self.get_selected_song_id()
        if song_id is None:
            messagebox.showwarning("No Selection", "Please select a song first.")
            return
        
        recommendations = self.ai_engine.get_content_based_recommendations(song_id, 8)
        self.display_recommendations(recommendations, "Similar Songs")
    
    def get_genre_recommendations(self):
        """Get recommendations based on selected genre"""
        genre = self.genre_var.get()
        if not genre:
            messagebox.showwarning("No Genre", "Please select a genre.")
            return
        
        recommendations = self.ai_engine.get_genre_based_recommendations([genre], 8)
        self.display_recommendations(recommendations, f"{genre} Recommendations")
    
    def get_personal_recommendations(self):
        """Get personalized recommendations"""
        recommendations = self.ai_engine.get_hybrid_recommendations(self.current_user, 8)
        self.display_recommendations(recommendations, "Personal Recommendations")
    
    def get_popular_recommendations(self):
        """Get popular song recommendations"""
        recommendations = self.ai_engine.get_popular_recommendations(8)
        self.display_recommendations(recommendations, "Popular Songs")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
