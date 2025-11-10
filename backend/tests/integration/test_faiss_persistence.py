"""Integration test for FAISS index persistence."""

from __future__ import annotations

import os
import tempfile
import uuid

import numpy as np
import pytest

from backend.src.vector.faiss_index import VectorIndex


def test_save_and_load_preserves_vectors():
    """Test that saving and loading FAISS index preserves vectors and IDs."""
    # Create a temporary file for the index
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = os.path.join(temp_dir, "test_index.bin")
        
        # Create index and add some vectors
        index1 = VectorIndex(dimension=768)
        section_ids = [str(uuid.uuid4()) for _ in range(5)]
        embeddings = np.random.rand(5, 768).astype("float32")
        
        index1.add(section_ids, embeddings)
        
        # Save the index
        index1.save(index_path)
        
        # Verify files were created
        assert os.path.exists(index_path), "Index file should be created"
        assert os.path.exists(index_path + ".meta"), "Metadata file should be created"
        
        # Create a new index and load from disk
        index2 = VectorIndex(dimension=768)
        index2.load(index_path)
        
        # Verify the IDs are preserved
        assert len(index2.ids) == 5, "Should have 5 section IDs"
        assert set(index2.ids) == set(section_ids), "Section IDs should match"
        
        # Verify we can search with the loaded index
        query = np.random.rand(1, 768).astype("float32")
        results = index2.search(query, k=3)
        
        assert len(results) == 3, "Should return 3 results"
        assert all(result_id in section_ids for result_id, _ in results), "All results should be valid section IDs"


def test_load_nonexistent_index():
    """Test that loading a nonexistent index starts with empty index."""
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = os.path.join(temp_dir, "nonexistent.bin")
        
        index = VectorIndex(dimension=768)
        index.load(index_path)  # Should not raise error
        
        assert len(index.ids) == 0, "Should have no IDs"
        assert index.index.ntotal == 0, "FAISS index should be empty"


def test_incremental_updates_with_persistence():
    """Test that we can load, add more vectors, and save again."""
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = os.path.join(temp_dir, "incremental.bin")
        
        # First batch
        index1 = VectorIndex(dimension=768)
        ids1 = [str(uuid.uuid4()) for _ in range(3)]
        emb1 = np.random.rand(3, 768).astype("float32")
        index1.add(ids1, emb1)
        index1.save(index_path)
        
        # Load and add second batch
        index2 = VectorIndex(dimension=768)
        index2.load(index_path)
        ids2 = [str(uuid.uuid4()) for _ in range(2)]
        emb2 = np.random.rand(2, 768).astype("float32")
        index2.add(ids2, emb2)
        index2.save(index_path)
        
        # Load again and verify all 5 vectors are present
        index3 = VectorIndex(dimension=768)
        index3.load(index_path)
        
        assert len(index3.ids) == 5, "Should have 5 total IDs"
        assert set(index3.ids) == set(ids1 + ids2), "Should have all section IDs"


def test_remove_and_persist():
    """Test that removing vectors and persisting works correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = os.path.join(temp_dir, "remove_test.bin")
        
        # Add vectors
        index1 = VectorIndex(dimension=768)
        ids = [str(uuid.uuid4()) for _ in range(5)]
        emb = np.random.rand(5, 768).astype("float32")
        index1.add(ids, emb)
        
        # Remove 2 vectors
        remove_ids = ids[:2]
        index1.remove(remove_ids)
        index1.save(index_path)
        
        # Load and verify only 3 remain
        index2 = VectorIndex(dimension=768)
        index2.load(index_path)
        
        assert len(index2.ids) == 3, "Should have 3 IDs after removal"
        assert all(id not in remove_ids for id in index2.ids), "Removed IDs should not be present"
