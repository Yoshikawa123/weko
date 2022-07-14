# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 National Institute of Informatics.
#
# weko-gridlayout is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""
import json
import pytest
from mock import patch, MagicMock
from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.base import ViewArgs

# import json
from weko_gridlayout.utils import get_register_language
from weko_gridlayout.admin import WidgetSettingView


@pytest.mark.parametrize("can_delete", [True, False, None])
def test_index_view_can_delete(app, client, admin_view, widget_items,
                               view_instance, can_delete):
    """Test flask-admin interace."""
    view = view_instance
    view.can_delete = can_delete
    index_view_url = url_for("widgetitem.index_view")
    res = client.get(index_view_url)
    assert res.status_code == 200


@pytest.mark.parametrize("sort", [1, None])
def test_index_view_sort_column(app,
                client, admin_view, view_instance, widget_items, sort):
    """Test flask-admin interace."""
    view = view_instance
    view_args = ViewArgs(page=1,
                        page_size=20,
                        sort=sort,
                        sort_desc=1,
                        search=None,
                        filters=None,
                        extra_args={})
    view.column_editable_list = {"test": "test"}

    with patch("weko_gridlayout.admin.WidgetSettingView._get_list_extra_args", return_value=view_args):
        index_view_url = url_for("widgetitem.index_view")
        res = client.get(index_view_url)
        assert res.status_code == 200


# with list-with data の場合にエラー発生
@pytest.mark.parametrize("condition1, condition2",
                         [("with list", "with data"), ("with list", "without data"),
                         ("without list", "with data"), ("without list", "without data"),
                         ("with page_size", "with count"), ("with page_size", "without count"),
                         ("without page_size", "with count"), ("without page_size", "without count")])
def test_index_view_editable_list_page_size_data(app, client, admin_view, view_instance,
                                widget_items, condition1, condition2):
    """Test flask-admin interace."""
    view = view_instance
    view_args = ViewArgs(page=1,
                        page_size=None,
                        sort=1,
                        sort_desc=1,
                        search=None,
                        filters=None,
                        extra_args={})
    if condition1 == "with list":
        view.column_editable_list = {"test": "test"}
    else:
        view.column_editable_list = {}

    if condition1 == "with page_size":
        view.page_size = 20
    else:
        view.page_size = None

    if condition2 == "with data" or condition2 == "with count":
        with patch("weko_gridlayout.admin.WidgetSettingView._get_list_extra_args", return_value=view_args):
            with patch("weko_gridlayout.admin.WidgetSettingView.get_list", return_value=(3, widget_items)):
                index_view_url = url_for("widgetitem.index_view")
                res = client.get(index_view_url)
                assert res.status_code == 200

    elif condition2 == "without count":
        with patch("weko_gridlayout.admin.WidgetSettingView.get_list", return_value=(None, widget_items)):
                index_view_url = url_for("widgetitem.index_view")
                res = client.get(index_view_url)
                assert res.status_code == 200
    else:
        index_view_url = url_for("widgetitem.index_view")
        res = client.get(index_view_url)
        assert res.status_code == 200


@pytest.mark.parametrize("page_size",
                         [1, 2])
def test_pager_url(app, client, admin_view, view_instance,
                   widget_items, page_size):
    """Test flask-admin interace."""
    view = view_instance
    view_args = ViewArgs(page=1,
                        page_size=page_size,
                        sort=1,
                        sort_desc=1,
                        search=None,
                        filters=None,
                        extra_args={})

    with patch("weko_gridlayout.admin.WidgetSettingView._get_list_extra_args", return_value=view_args):
        with patch("weko_gridlayout.admin.WidgetSettingView.get_list", return_value=(3, widget_items)):
            index_view_url = url_for("widgetitem.index_view")
            res = client.get(index_view_url)
            assert res.status_code == 200


#一つのパラメータセットにつき複数回呼び出されている模様
@pytest.mark.parametrize("desc, invert, sort_desc",
                         [(1, False, 1), (1, False, 0), (1, False, None),
                          (1, True, 1), (1, True, 0), (1, True, None),
                          (0, False, 1), (0, False, 0), (0, False, None),
                          (0, True, 1), (0, True, 0), (0, True, None),
                          (None, False, 1), (None, False, 0), (None, False, None),
                          (None, True, 1), (None, True, 0), (None, True, None),
                         ])
def test_sort_url(app, client, admin_view, view_instance,
                   widget_item, desc, invert, sort_desc):
    """Test flask-admin interace."""
    view = view_instance
    view_args = ViewArgs(page=1,
                        page_size=20,
                        sort=1,
                        sort_desc=sort_desc,
                        search=None,
                        filters=None,
                        extra_args={})
    view.desc = desc
    view.invert = invert
    with patch("weko_gridlayout.admin.WidgetSettingView._get_list_extra_args", return_value=view_args):
        with patch("weko_gridlayout.admin.WidgetSettingView.get_list", return_value=(1, widget_item)):
            index_view_url = url_for("widgetitem.index_view")
            res = client.get(index_view_url)
            assert res.status_code == 200
            if not desc and invert and not sort_desc:
                assert view.desc == 1
            else:
                assert view.desc == desc


@pytest.mark.parametrize("page_size",
                         [20, 0, None])
def test_page_size_url(app, client, admin_view, view_instance,
                   widget_item, page_size):
    """Test flask-admin interace."""
    view = view_instance
    view_args = ViewArgs(page=1,
                        page_size=page_size,
                        sort=1,
                        sort_desc=1,
                        search=None,
                        filters=None,
                        extra_args={})
    view.page_size = page_size
    with patch("weko_gridlayout.admin.WidgetSettingView._get_list_extra_args", return_value=view_args):
        with patch("weko_gridlayout.admin.WidgetSettingView.get_list", return_value=(1, widget_item)):
            index_view_url = url_for("widgetitem.index_view")
            res = client.get(index_view_url)
            assert res.status_code == 200


def test_get_label_display_to_list_without_register_languages(admin_view, widget_items):
    res = WidgetSettingView.get_label_display_to_list(1)
    assert res == None


@pytest.mark.parametrize("num, result",
                         [(1, None), (2, None)])
def test_get_label_display_to_list_without_widget(admin_view, admin_lang_settings, num, result):
    res = WidgetSettingView.get_label_display_to_list(num)
    assert res == result


@pytest.mark.parametrize("num, result",
                         [(1, "for test"), (2, "for test2"), (3, None)])
def test_get_label_display_to_list(admin_view, widget_items, admin_lang_settings, num, result):
    res = WidgetSettingView.get_label_display_to_list(num)
    assert res == result


def test_search_placeholder(app, admin_view, widget_items, view_instance):
    assert view_instance.search_placeholder() == "Search"