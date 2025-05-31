import axios from 'axios';

const TMDB_BASE_URL = 'https://api.themoviedb.org/3';
const API_KEY = process.env.REACT_APP_TMDB_API_KEY;

// Create axios instance with default config
const tmdbApi = axios.create({
  baseURL: TMDB_BASE_URL,
  params: {
    api_key: API_KEY,
    language: 'en-US',
  },
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_path: string;
  genre_ids: number[];
  vote_average: number;
  release_date: string;
  streaming_services?: string[];
}

export const tmdbService = {
  // Get popular movies that are available for streaming
  getStreamingMovies: async (page = 1): Promise<Movie[]> => {
    try {
      // Get movies available on streaming platforms (Netflix/Amazon Prime)
      const response = await tmdbApi.get('/discover/movie', {
        params: {
          page,
          with_watch_providers: '8|9', // Netflix (8) and Prime Video (9)
          watch_region: 'US',
          sort_by: 'popularity.desc',
        },
      });
      return response.data.results;
    } catch (error) {
      console.error('Error fetching streaming movies:', error);
      return [];
    }
  },

  // Get movie details
  getMovieDetails: async (movieId: number): Promise<Movie | null> => {
    try {
      const response = await tmdbApi.get(`/movie/${movieId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching movie details:', error);
      return null;
    }
  },

  // Get movie genres
  getGenres: async () => {
    try {
      const response = await tmdbApi.get('/genre/movie/list');
      return response.data.genres;
    } catch (error) {
      console.error('Error fetching genres:', error);
      return [];
    }
  },

  // Get streaming providers for a movie
  getStreamingProviders: async (movieId: number) => {
    try {
      const response = await tmdbApi.get(`/movie/${movieId}/watch/providers`);
      return response.data.results.US;
    } catch (error) {
      console.error('Error fetching streaming providers:', error);
      return null;
    }
  },
}; 