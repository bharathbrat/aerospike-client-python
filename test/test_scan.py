# -*- coding: utf-8 -*-

import pytest
import sys

try:
    import aerospike
except:
    print "Please install aerospike python client."
    sys.exit(1)


class TestScan(object):

    def setup_method(self, method):

        """
        Setup method.
        """
        config = {
                'hosts': [('127.0.0.1', 3000)]
                }
        self.client = aerospike.client(config).connect()

        for i in xrange(20):
            key = ('test', u'demo', i)
            rec = {
                    'name' : 'name%s' % (str(i)),
                    'age'  : i
                    }
            self.client.put(key, rec)

    def teardown_method(self, method):

        """
        Teardown method
        """

        for i in xrange(20):
            key = ('test', u'demo', i)
            self.client.remove(key)

        self.client.close()

    def test_scan_without_any_parameter(self):


        with pytest.raises(TypeError) as typeError:
            scan_obj = self.client.scan()
            scan_obj.foreach()

        assert "Required argument 'callback' (pos 1) not found" in typeError.value

    def test_scan_with_non_existent_ns_and_set(self):

        ns = 'namespace'
        st = 'set'

        records = []

        scan_obj = self.client.scan(ns, st)

        def callback( (key, meta, bins) ):
            records.append(bins)

        with pytest.raises(Exception) as exception:
            scan_obj.foreach(callback)

        assert exception.value[0] == 1L
        assert exception.value[1] == 'AEROSPIKE_ERR_SERVER'

    def test_scan_with_none_ns_and_set(self):

        ns = None
        st = None

        with pytest.raises(Exception) as exception:
            scan_obj = self.client.scan( ns, st )

        assert exception.value[0] == -1L
        assert exception.value[1] == 'Parameters are incorrect'

    def test_scan_with_existent_ns_and_set(self):

        ns = 'test'
        st = 'demo'

        records = []

        def callback( (key, meta, bins) ):
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.foreach(callback)

        assert len(records) != 0

    def test_scan_with_timeout_policy(self):

        ns = 'test'
        st = 'demo'

        records = []

        def callback( (key, meta, bins) ):
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.foreach(callback, { 'timeout' : 2000 })

        assert len(records) != 0
    """
    def test_scan_with_callback_contains_error(self):

            #Invoke scan() with callback function returns false
        ns = 'test'
        st = 'demo'

        records = []
        val = 1
        def callback( (key, meta, bins) ):
            val += 1
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.foreach(callback, { 'timeout' : 1000 })

        assert len(records) == 0
    """

    def test_scan_with_callback_returning_false(self):

        """
            Invoke scan() with callback function returns false
        """
        ns = 'test'
        st = 'demo'

        records = []

        def callback( (key, meta, bins) ):
            if len(records) == 10:
                return False
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.foreach(callback , {'timeout' : 1000})
        assert len(records) == 10

    def test_scan_with_unicode_set(self):

        ns = 'test'

        st = u'demo'

        records = []

        def callback( (key, meta, bins) ):
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.foreach(callback)

        assert len(records) != 0

    def test_scan_with_select_clause(self):

        ns = 'test'
        st = 'demo'

        records = []

        def callback( (key, meta, bins) ):
            records.append(bins)

        scan_obj = self.client.scan(ns, st)

        scan_obj.select('name')

        scan_obj.foreach(callback)

        assert len(records) != 0

    def test_scan_with_results_method(self):

        ns = 'test'
        st = 'demo'

        records = []

        scan_obj = self.client.scan(ns, st)

        scan_obj.select(u'name', u'age')

        records = scan_obj.results()

        assert len(records) != 0

    def test_scan_with_select_bin_integer(self):

        """
            Invoke scan() with select bin is of type integer.
        """
        scan_obj = self.client.scan('test', 'demo')

        with pytest.raises(Exception) as exception:
            scan_obj.select(22, 'test_age')

        assert exception.value[0] == -2L
        assert exception.value[1] == 'Bin name should be of type string'
