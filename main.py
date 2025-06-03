from frontend.gui import MusicRecommendationGUI

def main():
    """Main application entry point"""
    print("🎵 Starting AI Music Recommendation System...")
    print("Loading database and AI models...")
    
    app = MusicRecommendationGUI()
    app.run()

if __name__ == "__main__":
    main()