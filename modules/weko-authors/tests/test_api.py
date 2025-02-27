from mock import patch
import json
import pytest
from invenio_indexer.api import RecordIndexer

from weko_authors.api import WekoAuthors
from weko_authors.models import Authors, AuthorsPrefixSettings
from weko_authors.config import WEKO_AUTHORS_FILE_MAPPING

# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp

class MockClient():
    def __init__(self):
        self.index_ = self.MockIndex()
        self.return_value=""
    def index(self,index,doc_type,body):
        return self.index_
    def delete(self,index,doc_type,id):
        pass
    def set_return(self,value):
        self.return_value=value
    def search(self,index,doc_type,body):
        return self.return_value
    def update(self,index,doc_type,id,body):
        pass
    class MockIndex():
        def __init__(self):
            self.data = {}
        def get(self,type,value):
            return self.data.get(type)
        def set(self,type,data):
            self.data[type]=data

# class WekoAuthors(object):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
class TestWekoAuthors:
#     def create(cls, data):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_create -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_create(self,app,db,mocker):
        mocker.patch("weko_authors.api.Authors.get_sequence",return_value=1)
        record_indexer = RecordIndexer()
        record_indexer.client = MockClient()
        record_indexer.client.index("","","").set("_id",1)
        mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
        data = {
            "authorIdInfo":[]
        }
        WekoAuthors.create(data)
        test ='{"authorIdInfo": [{"authorId": "1", "authorIdShowFlg": "true", "idType": "1"}], "gather_flg": 0, "id": 1, "pk_id": "1"}'
        result = Authors.query.filter_by(id=1).one()
        assert result.id == 1
        assert result.json == test
        
        with patch("weko_authors.api.db.session.add",side_effect=Exception("test_error")):
            data = {
                "authorIdInfo":[]
            }
            with pytest.raises(Exception):
                result = WekoAuthors.create(data)
            
        
            record_indexer = RecordIndexer()
            record_indexer.client = MockClient()
            mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
            data = {
                "authorIdInfo":[]
            }
            with pytest.raises(Exception):
                result = WekoAuthors.create(data)
            
#     def update(cls, author_id, data):
#         def update_es_data(data):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_update(self,app,authors,mocker):
        author_id=1
        
        # is_deleted is false, 
        data={"is_deleted":False}
        record_indexer = RecordIndexer()
        record_indexer.client = MockClient()
        record_indexer.client.set_return({"hits":{"total":1,"hits":[{"_id":1}]}})
        mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
        WekoAuthors.update(author_id,data)

        data={"is_deleted":True}
        record_indexer.client.index("","","").set("_id",1)
        record_indexer.client.set_return({"hits":{"total":0,"hits":[]}})
        mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
        WekoAuthors.update(author_id,data)
        
        # raise Exception, es_id is None
        record_indexer.client.set_return({"hits":{"total":1,"hits":[{"_id":1}]}})
        mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
        with pytest.raises(Exception):
            WekoAuthors.update(1000,data)

        # raise Exception , es_id is not None
        data = {"is_deleted":False}
        record_indexer = RecordIndexer()
        record_indexer.client = MockClient()
        record_indexer.client.set_return({"hits":{"total":1,"hits":[{"_id":1}]}})
        mocker.patch("weko_authors.api.RecordIndexer",return_value=record_indexer)
        with patch("weko_authors.api.db.session.merge",side_effect=Exception):
            with pytest.raises(Exception):
                WekoAuthors.update(author_id,data)
            
#     def get_all(cls, with_deleted=True, with_gather=True):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_get_all -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_get_all(self,app,authors):
        result = WekoAuthors.get_all()
        assert authors
        result = WekoAuthors.get_all(False,False)
        assert authors
#     def get_author_for_validation(cls):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_get_author_for_validation -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_get_author_for_validation(self,authors,mocker):
        mocker.patch("weko_authors.api.WekoAuthors.get_all",return_value=authors)
        
        authors_result, external_result = WekoAuthors.get_author_for_validation()
        assert authors_result == {"1":True,"2":True}
        assert external_result == {"2":{"1234":["1"],"5678":["2"]}}

#     def get_identifier_scheme_info(cls):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_get_identifier_scheme_info -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_get_identifier_scheme_info(self,db,authors_prefix_settings):
        test = {
            "1":{"scheme":"WEKO","url":None},
            "2":{"scheme":"ORCID","url":"https://orcid.org/##"},
            "3":{"scheme":"CiNii","url":"https://ci.nii.ac.jp/author/##"},
            "4":{"scheme":"KAKEN2","url":"https://nrid.nii.ac.jp/nrid/##"},
            "5":{"scheme":"ROR","url":"https://ror.org/##"}
        }
        result = WekoAuthors.get_identifier_scheme_info()
        assert result == test
        
        AuthorsPrefixSettings.query.delete()
        db.session.commit()
        result = WekoAuthors.get_identifier_scheme_info()
        assert result == {}
        
#     def prepare_export_data(cls, mappings, authors, schemes):
# .tox/c1/bin/pytest --cov=weko_authors tests/test_api.py::TestWekoAuthors::test_prepare_export_data -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-authors/.tox/c1/tmp
    def test_prepare_export_data(self,db, authors,mocker):
        mocker.patch("weko_authors.api.WekoAuthors.get_all",return_value=authors)
        scheme_info={"1":{"scheme":"WEKO","url":None},"2":{"scheme":"ORCID","url":"https://orcid.org/##"}}
        mocker.patch("weko_authors.api.WekoAuthors.get_identifier_scheme_info",return_value=scheme_info)
        header, label_en,label_jp,data = WekoAuthors.prepare_export_data(None,None,None)
        assert header == ["#pk_id","authorNameInfo[0].familyName","authorNameInfo[0].firstName","authorNameInfo[0].language","authorNameInfo[0].nameFormat","authorNameInfo[0].nameShowFlg","authorIdInfo[0].idType","authorIdInfo[0].authorId","authorIdInfo[0].authorIdShowFlg","emailInfo[0].email","is_deleted"]
        assert label_en == ["#WEKO ID","Family Name[0]","Given Name[0]","Language[0]","Name Format[0]","Name Display[0]","Identifier Scheme[0]","Identifier[0]","Identifier Display[0]","Mail Address[0]","Delete Flag"]
        assert label_jp == ["#WEKO ID","姓[0]","名[0]","言語[0]","フォーマット[0]","姓名・言語 表示／非表示[0]","外部著者ID 識別子[0]","外部著者ID[0]","外部著者ID 表示／非表示[0]","メールアドレス[0]","削除フラグ"]
        
        assert data == [["1","テスト","太郎","ja","familyNmAndNm","Y","ORCID","1234","Y","test.taro@test.org",""],
                        ["2","test","smith","en","familyNmAndNm","Y","ORCID","5678","Y","test.smith@test.org",""]]

        # authors is false
        mocker.patch("weko_authors.api.WekoAuthors.get_all",return_value=[])
        header, label_en,label_jp,data = WekoAuthors.prepare_export_data(None,None,None)
        assert header == ["#pk_id","authorNameInfo[0].familyName","authorNameInfo[0].firstName","authorNameInfo[0].language","authorNameInfo[0].nameFormat","authorNameInfo[0].nameShowFlg","authorIdInfo[0].idType","authorIdInfo[0].authorId","authorIdInfo[0].authorIdShowFlg","emailInfo[0].email","is_deleted"]
        assert label_en == ["#WEKO ID","Family Name[0]","Given Name[0]","Language[0]","Name Format[0]","Name Display[0]","Identifier Scheme[0]","Identifier[0]","Identifier Display[0]","Mail Address[0]","Delete Flag"]
        assert label_jp == ["#WEKO ID","姓[0]","名[0]","言語[0]","フォーマット[0]","姓名・言語 表示／非表示[0]","外部著者ID 識別子[0]","外部著者ID[0]","外部著者ID 表示／非表示[0]","メールアドレス[0]","削除フラグ"]
        
        assert data == []
        
        
        author = {
            "authorNameInfo":[],
            "authorIdInfo":[],
            "emailInfo":[]
        }
        a = Authors(
            gather_flg=0,
            is_deleted=False,
            json=json.dumps(author)
        )
        mapping = WEKO_AUTHORS_FILE_MAPPING
        header, label_en,label_jp,data = WekoAuthors.prepare_export_data(mapping,[a],scheme_info)
        
        assert header == ["#pk_id","authorNameInfo[0].familyName","authorNameInfo[0].firstName","authorNameInfo[0].language","authorNameInfo[0].nameFormat","authorNameInfo[0].nameShowFlg","authorIdInfo[0].idType","authorIdInfo[0].authorId","authorIdInfo[0].authorIdShowFlg","emailInfo[0].email","is_deleted"]
        assert label_en == ["#WEKO ID","Family Name[0]","Given Name[0]","Language[0]","Name Format[0]","Name Display[0]","Identifier Scheme[0]","Identifier[0]","Identifier Display[0]","Mail Address[0]","Delete Flag"]
        assert label_jp == ["#WEKO ID","姓[0]","名[0]","言語[0]","フォーマット[0]","姓名・言語 表示／非表示[0]","外部著者ID 識別子[0]","外部著者ID[0]","外部著者ID 表示／非表示[0]","メールアドレス[0]","削除フラグ"]
        
        assert data == [[None,None,None,None,None,None,None,None,None,None,None]]
        
        
