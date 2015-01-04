from __future__ import absolute_import

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from documents.models import Document, DocumentType
from ocr.parsers import parse_document_page

from .classes import SearchModel

TEST_ADMIN_PASSWORD = 'test_admin_password'
TEST_ADMIN_USERNAME = 'test_admin'
TEST_ADMIN_EMAIL = 'admin@admin.com'
TEST_SMALL_DOCUMENT_FILENAME = 'title_page.png'
TEST_DOCUMENT_PATH = os.path.join(settings.BASE_DIR, 'contrib', 'sample_documents', 'mayan_11_1.pdf')
TEST_SIGNED_DOCUMENT_PATH = os.path.join(settings.BASE_DIR, 'contrib', 'sample_documents', 'mayan_11_1.pdf.gpg')
TEST_SMALL_DOCUMENT_PATH = os.path.join(settings.BASE_DIR, 'contrib', 'sample_documents', TEST_SMALL_DOCUMENT_FILENAME)
TEST_DOCUMENT_DESCRIPTION = 'test description'
TEST_DOCUMENT_TYPE = 'test_document_type'

document_search = SearchModel.get('documents.Document')

'''
class DocumentSearchTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL, password=TEST_ADMIN_PASSWORD)

        self.document_type = DocumentType(name=TEST_DOCUMENT_TYPE)
        self.document_type.save()

        self.document = Document(
            document_type=self.document_type,
        )
        self.document.save()

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document.new_version(file_object=File(file_object, name='mayan_11_1.pdf'))

        # Text extraction on the first page only
        parse_document_page(self.document.latest_version.pages.all()[0])

    def test_simple_search_after_related_name_change(self):
        """
        Test that simple search works after related_name changes to
        document versions and document version pages
        """

        model_list, result_set, elapsed_time = document_search.search({'q':'Mayan'}, user=self.admin_user)
        self.assertEqual(len(result_set), 1)
        self.assertEqual(model_list, [self.document])

    def test_advanced_search_after_related_name_change(self):
        # Test versions__filename
        model_list, result_set, elapsed_time = document_search.search({'label': self.document.label}, user=self.admin_user)
        self.assertEqual(len(result_set), 1)
        self.assertEqual(model_list, [self.document])

        # Test versions__mimetype
        model_list, result_set, elapsed_time = document_search.search({'versions__mimetype': self.document.file_mimetype}, user=self.admin_user)
        self.assertEqual(len(result_set), 1)
        self.assertEqual(model_list, [self.document])

        # Test versions__pages__content
        # Search by the first 20 characters of the content of the first page of the uploaded document
        model_list, result_set, elapsed_time = document_search.search({'versions__pages__content': self.document.latest_version.pages.all()[0].content[0:20]}, user=self.admin_user)
        self.assertEqual(len(result_set), 1)
        self.assertEqual(model_list, [self.document])

    def tearDown(self):
        self.document.delete()
        self.document_type.delete()
'''

class Issue46TestCase(TestCase):
    """
    Functional tests to make sure issue 46 is fixed
    """

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL, password=TEST_ADMIN_PASSWORD)
        self.client = Client()
        # Login the admin user
        logged_in = self.client.login(username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD)
        self.assertTrue(logged_in)
        self.assertTrue(self.admin_user.is_authenticated())

        self.document_count = 30

        self.document_type = DocumentType.objects.create(name='test doc type')

        # Upload 30 instances of the same test document
        for i in range(self.document_count):
            with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
                Document.objects.new_document(
                    file_object=File(file_object),
                    label='test document',
                    document_type=self.document_type
                )

    def test_advanced_search_past_first_page(self):

        # Make sure all documents are returned by the search
        model_list, result_set, elapsed_time = document_search.search({'label': 'test document'}, user=self.admin_user)
        self.assertEqual(len(result_set), self.document_count)

        # Funcitonal test for the first page of advanced results
        response = self.client.get(reverse('search:results'), {'label': 'test'})
        self.assertTrue('esults (1 - 20 out of 30) (Page 1 of 2)' in response.content)

        # Functional test for the second page of advanced results
        response = self.client.get(reverse('search:results'), {'label': 'test', 'page': 2})
        self.assertTrue('esults (21 - 30 out of 30) (Page 2 of 2)' in response.content)
