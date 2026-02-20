import { useState, useEffect } from 'react';
import { supabase } from '../services/supabase';
import type { LocationRow } from '../types';

export function useLocations() {
  const [locations, setLocations] = useState<LocationRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetch() {
      try {
        const { data, error } = await supabase
          .from('locations')
          .select('*')
          .order('name');
        if (error) throw error;
        setLocations(data as LocationRow[]);
      } catch (err) {
        console.error('Failed to load locations:', err);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, []);

  return { locations, loading };
}
