#!/usr/bin/env python3
# coding: utf-8

import os
import tempfile
import unittest
from pathlib import Path
from typing import Union
from unittest.mock import Mock, patch, mock_open

import pytest
import requests

# Import the functions we want to test
from gofilepy.gofile import upload, gofile_upload


class TestGofileUpload(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_server = "store1"
        self.test_token = "test_token_123"
        self.test_folder_id = "folder_123"

        # Create a temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write("Test file content")
        self.temp_file.close()
        self.test_file_path = self.temp_file.name

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary test file
        if os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)

    @pytest.mark.parametrize("verbose", [0, 1, 2, True, False])
    @patch('gofilepy.gofile.requests.post')
    @patch.dict(os.environ, {'GOFILE_TOKEN': 'test_token_123'})
    def test_upload_successful(self, mock_post: Mock, verbose: Union[int, bool]):
        """Test successful file upload with different verbose levels."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'downloadPage': 'https://gofile.io/d/test123',
                'code': 'test123',
                'parentFolder': 'folder_456'
            }
        }
        mock_post.return_value = mock_response

        # Call the upload function
        result = upload(self.test_file_path, self.test_server, self.test_folder_id, verbose=verbose)

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        expected_url = f'https://{self.test_server}.gofile.io/uploadFile'
        self.assertEqual(call_args[0][0], expected_url)

        # Check data parameters
        self.assertEqual(call_args[1]['data']['token'], 'test_token_123')
        self.assertEqual(call_args[1]['data']['folderId'], self.test_folder_id)

        # Check file parameter
        self.assertIn('file', call_args[1]['files'])
        file_tuple = call_args[1]['files']['file']
        self.assertEqual(file_tuple[0], Path(self.test_file_path).name)
        self.assertEqual(file_tuple[2], 'text/plain')  # MIME type for .txt file

        # Verify response and return value structure
        self.assertEqual(result, mock_response)
        response_data = result.json()
        self.assertEqual(response_data['status'], 'ok')
        self.assertIn('downloadPage', response_data['data'])
        self.assertIn('code', response_data['data'])
        self.assertIn('parentFolder', response_data['data'])

    @pytest.mark.parametrize("verbose", [0, 1, 2, True, False])
    @patch('gofilepy.gofile.requests.post')
    @patch('gofilepy.gofile.time.sleep')
    @patch('gofilepy.gofile.rprint')
    def test_upload_with_connection_retry(self, mock_rprint: Mock, mock_sleep: Mock, mock_post: Mock, verbose: Union[int, bool]):
        """Test upload with connection error retry logic and different verbose levels."""
        # First two calls raise ConnectionError, third succeeds
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'ok', 'data': {'downloadPage': 'test'}}

        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response
        ]

        result = upload(self.test_file_path, self.test_server, verbose=verbose)

        # Should have made 3 attempts
        self.assertEqual(mock_post.call_count, 3)
        # Should have slept twice (after first two failures)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(2)

        # Check verbose behavior
        if verbose:
            # Should have printed retry messages
            self.assertEqual(mock_rprint.call_count, 2)
        else:
            # Should not print when verbose is 0 or False
            mock_rprint.assert_not_called()

        # Should return successful response
        self.assertEqual(result, mock_response)
        # Check return value structure
        response_data = result.json()
        self.assertEqual(response_data['status'], 'ok')
        self.assertIn('downloadPage', response_data['data'])

    @patch('gofilepy.gofile.requests.post')
    @patch('gofilepy.gofile.time.sleep')
    def test_upload_max_retries_exceeded(self, mock_sleep: Mock, mock_post: Mock):
        """Test upload when max retries are exceeded."""
        # Always raise ConnectionError
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = upload(self.test_file_path, self.test_server)

        # Should have made 11 attempts (initial + 10 retries)
        self.assertEqual(mock_post.call_count, 11)
        # Should have slept 10 times
        self.assertEqual(mock_sleep.call_count, 10)
        # Result should be None (function returns after break)
        self.assertIsNone(result)

    @pytest.mark.parametrize("verbose", [0, 1, 2])
    @patch('gofilepy.gofile.requests.get')
    @patch('gofilepy.gofile.upload')
    def test_gofile_upload_single_file(self, mock_upload: Mock, mock_get: Mock, verbose: int):
        """Test gofile_upload function with a single file and different verbose levels."""
        # Mock server selection
        mock_get.return_value.json.return_value = {
            'data': {
                'servers': [{'name': 'store1'}]
            }
        }

        # Mock upload response
        mock_upload_response = Mock()
        mock_upload_response.json.return_value = {
            'status': 'ok',
            'data': {
                'downloadPage': 'https://gofile.io/d/test123',
                'parentFolder': 'folder_456'
            }
        }
        mock_upload.return_value = mock_upload_response

        # Call gofile_upload and check return values
        with patch('gofilepy.gofile.track') as mock_track:
            mock_track.return_value = [self.test_file_path]  # Mock the progress tracker
            urls, export_data = gofile_upload([self.test_file_path], verbose=verbose)

        # Verify server selection API call
        mock_get.assert_called_once_with('https://api.gofile.io/servers')

        # Verify upload was called with correct parameters
        mock_upload.assert_called_once_with(self.test_file_path, 'store1', None)

        # Check return values
        self.assertIsInstance(urls, list)
        self.assertIsInstance(export_data, list)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'https://gofile.io/d/test123')
        self.assertEqual(len(export_data), 0)  # Empty when export=False

    @patch('gofilepy.gofile.requests.get')
    @patch('gofilepy.gofile.upload')
    @patch.dict(os.environ, {'GOFILE_TOKEN': 'test_token_123'})
    def test_gofile_upload_to_single_folder(self, mock_upload: Mock, mock_get: Mock):
        """Test gofile_upload with to_single_folder option."""
        # Mock server selection
        mock_get.return_value.json.return_value = {
            'data': {
                'servers': [{'name': 'store1'}]
            }
        }

        # Mock upload responses
        mock_upload_responses = []
        for i in range(2):
            mock_response = Mock()
            mock_response.json.return_value = {
                'status': 'ok',
                'data': {
                    'downloadPage': f'https://gofile.io/d/test{i}',
                    'parentFolder': 'shared_folder_123'
                }
            }
            mock_upload_responses.append(mock_response)

        mock_upload.side_effect = mock_upload_responses

        # Create second test file
        temp_file2 = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file2.write("Second test file")
        temp_file2.close()

        try:
            with patch('gofilepy.gofile.track') as mock_track:
                mock_track.return_value = [self.test_file_path, temp_file2.name]
                urls, export_data = gofile_upload([self.test_file_path, temp_file2.name], to_single_folder=True)

            # Verify first upload called with None folder_id
            first_call = mock_upload.call_args_list[0]
            self.assertEqual(first_call[0], (self.test_file_path, 'store1', None))

            # Verify second upload called with folder_id from first response
            second_call = mock_upload.call_args_list[1]
            self.assertEqual(second_call[0], (temp_file2.name, 'store1', 'shared_folder_123'))

            # Check return values
            self.assertIsInstance(urls, list)
            self.assertIsInstance(export_data, list)
            self.assertEqual(len(urls), 2)
            self.assertEqual(urls[0], 'https://gofile.io/d/test0')
            self.assertEqual(urls[1], 'https://gofile.io/d/test1')
            self.assertEqual(len(export_data), 0)  # Empty when export=False

        finally:
            os.unlink(temp_file2.name)

    @patch('gofilepy.gofile.requests.get')
    @patch('gofilepy.gofile.upload')
    @patch('gofilepy.gofile.sys.exit')
    @patch('gofilepy.gofile.rprint')
    def test_gofile_upload_single_folder_without_token(self, mock_rprint: Mock, mock_exit: Mock, mock_upload: Mock, mock_get: Mock):
        """Test gofile_upload with to_single_folder but without token."""
        # Mock server selection
        mock_get.return_value.json.return_value = {
            'data': {
                'servers': [{'name': 'store1'}]
            }
        }

        # Mock upload response
        mock_upload_response = Mock()
        mock_upload_response.json.return_value = {
            'status': 'ok',
            'data': {
                'downloadPage': 'https://gofile.io/d/test123',
                'parentFolder': 'folder_456'
            }
        }
        mock_upload.return_value = mock_upload_response

        # Ensure no token is set
        with patch.dict(os.environ, {}, clear=True):
            with patch('gofilepy.gofile.track') as mock_track:
                mock_track.return_value = [self.test_file_path]
                gofile_upload([self.test_file_path], to_single_folder=True)

        # Should print error message and exit
        mock_rprint.assert_called()
        mock_exit.assert_called_with(1)

    @patch('gofilepy.gofile.requests.get')
    @patch('gofilepy.gofile.upload')
    @patch('gofilepy.gofile.json.dump')
    def test_gofile_upload_with_export(self, mock_json_dump: Mock, mock_upload: Mock, mock_get: Mock):
        """Test gofile_upload with export option."""
        # Mock server selection
        mock_get.return_value.json.return_value = {
            'data': {
                'servers': [{'name': 'store1'}]
            }
        }

        # Mock upload response
        mock_upload_response = Mock()
        upload_data = {
            'status': 'ok',
            'data': {
                'downloadPage': 'https://gofile.io/d/test123',
                'parentFolder': 'folder_456'
            }
        }
        mock_upload_response.json.return_value = upload_data
        mock_upload.return_value = mock_upload_response

        with patch('gofilepy.gofile.track') as mock_track, \
                patch('builtins.open', mock_open()) as mock_file:
            mock_track.return_value = [self.test_file_path]
            urls, export_data = gofile_upload([self.test_file_path], export=True)

        # Verify JSON export was called
        mock_json_dump.assert_called_once()
        export_call_args = mock_json_dump.call_args[0]
        exported_data = export_call_args[0]

        # Check exported data structure
        self.assertEqual(len(exported_data), 1)
        record = exported_data[0]
        self.assertIn('file', record)
        self.assertIn('timestamp', record)
        self.assertIn('response', record)
        self.assertEqual(record['response'], upload_data)

        # Check return values
        self.assertIsInstance(urls, list)
        self.assertIsInstance(export_data, list)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'https://gofile.io/d/test123')
        # Check that export_data from return value matches what was exported
        self.assertEqual(len(export_data), 1)
        self.assertEqual(export_data[0]['response'], upload_data)

    def test_upload_file_not_exists(self):
        """Test upload with non-existent file."""
        non_existent_file = "/path/to/non/existent/file.txt"

        with self.assertRaises(FileNotFoundError):
            upload(non_existent_file, self.test_server)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
