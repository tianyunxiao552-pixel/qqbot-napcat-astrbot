import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
ASTRBOT=Path(os.environ.get('QQBOT_TEST_ASTRBOT', str(ROOT/'AstrBot')))
os.chdir(ASTRBOT)
sys.path.insert(0,str(ASTRBOT))
from PIL import Image as PillowImage
from astrbot.core.agent.message import TextPart
from astrbot.core.message.components import File, Reply, Image
from astrbot.core.provider.entities import ProviderRequest

spec=importlib.util.spec_from_file_location('qq_image_files_test',ROOT/'AstrBot/data/plugins/astrbot_plugin_qq_image_files/main.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ImageFileTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)
        self.image=self.path/'picture.png'
        PillowImage.new('RGB',(30,30),'blue').save(self.image)
        self.document=self.path/'document.txt'
        self.document.write_text('A regular text attachment',encoding='utf-8')
        self.plugin=module.Main.__new__(module.Main)
    def tearDown(self): self.temp.cleanup()
    def event(self,parts,platform='aiocqhttp'):
        return SimpleNamespace(get_platform_name=lambda:platform,get_messages=lambda:parts)
    def notice(self,file,quoted=False):
        prefix='File Attachment in quoted message' if quoted else 'File Attachment'
        return TextPart(text=f'[{prefix}: name {file.name}, path {Path(file.file_).resolve()}]')

    async def test_image_file_reaches_vision_without_rewriting_persona(self):
        f=File(name='picture.png',file=str(self.image))
        req=ProviderRequest(prompt='<attachment>',system_prompt='汐见萤第19话人格',extra_user_content_parts=[self.notice(f)])
        await self.plugin.promote_image_files(self.event([f]),req)
        self.assertEqual(req.image_urls,[str(self.image.resolve())])
        self.assertEqual(req.extra_user_content_parts,[])
        self.assertEqual(req.prompt,'')
        self.assertEqual(req.system_prompt,'汐见萤第19话人格')

    async def test_mixed_documents_are_preserved(self):
        image=File(name='picture.png',file=str(self.image))
        doc=File(name='document.txt',file=str(self.document))
        req=ProviderRequest(prompt='帮我看看这两个',extra_user_content_parts=[self.notice(image),self.notice(doc)])
        await self.plugin.promote_image_files(self.event([image,doc]),req)
        self.assertEqual(req.image_urls,[str(self.image.resolve())])
        self.assertEqual([p.text for p in req.extra_user_content_parts],[self.notice(doc).text])
        self.assertEqual(req.prompt,'帮我看看这两个')

    async def test_file_content_determines_image_type(self):
        disguised=self.path/'photo.bin';disguised.write_bytes(self.image.read_bytes())
        false_image=self.path/'not_really.png';false_image.write_text('not an image')
        image=File(name='photo.bin',file=str(disguised))
        doc=File(name='not_really.png',file=str(false_image))
        req=ProviderRequest(prompt='<attachment>',extra_user_content_parts=[self.notice(image),self.notice(doc)])
        await self.plugin.promote_image_files(self.event([image,doc]),req)
        self.assertEqual(req.image_urls,[str(disguised.resolve())])
        self.assertEqual([p.text for p in req.extra_user_content_parts],[self.notice(doc).text])

    async def test_quoted_file_image(self):
        f=File(name='picture.png',file=str(self.image))
        reply=Reply(id='1',chain=[f])
        req=ProviderRequest(prompt='这张呢',extra_user_content_parts=[self.notice(f,quoted=True)])
        await self.plugin.promote_image_files(self.event([reply]),req)
        self.assertEqual(req.image_urls,[str(self.image.resolve())])
        self.assertEqual(req.extra_user_content_parts,[])

    async def test_existing_images_are_not_duplicated(self):
        f=File(name='picture.png',file=str(self.image))
        req=ProviderRequest(prompt='看看',image_urls=[str(self.image.resolve())])
        event=self.event([Image.fromFileSystem(self.image),f])
        await self.plugin.promote_image_files(event,req)
        await self.plugin.promote_image_files(event,req)
        self.assertEqual(req.image_urls,[str(self.image.resolve())])

    async def test_other_platforms_unchanged(self):
        f=File(name='picture.png',file=str(self.image))
        req=ProviderRequest(prompt='<attachment>',extra_user_content_parts=[self.notice(f)])
        await self.plugin.promote_image_files(self.event([f],platform='webchat'),req)
        self.assertEqual(req.image_urls,[])
        self.assertEqual(len(req.extra_user_content_parts),1)

unittest.main(verbosity=2)
