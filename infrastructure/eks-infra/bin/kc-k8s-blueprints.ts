#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { KcClusterConstruct } from '../lib/kc-k8s-blueprints-stack';

const app = new cdk.App();
const account = process.env.CDK_DEFAULT_ACCOUNT!;
const region = process.env.CDK_DEFAULT_REGION;
const stage = app.node.tryGetContext('stage') || ''; // default for dev env, cluster name: kc-cluster
const env = { account, region }

new KcClusterConstruct(app, `kc-cluster${stage}`, { env });